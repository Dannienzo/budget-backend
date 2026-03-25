# user/signals.py
from decimal import Decimal
from django.db import transaction as db_transaction
from django.db.models import Sum
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Transaction, Budget


@receiver(pre_save, sender=Transaction)
def transaction_pre_save(sender, instance, **kwargs):
    """
    Save a snapshot of the previous Transaction record (if any) so we can
    compare previous values when handling updates in post_save.
    """
    if not instance.pk:
        instance._pre_save_snapshot = None
        return

    try:
        prev = Transaction.objects.get(pk=instance.pk)
        instance._pre_save_snapshot = prev
    except Transaction.DoesNotExist:
        instance._pre_save_snapshot = None


@receiver(post_save, sender=Transaction)
def transaction_post_save(sender, instance, created, **kwargs):
    """
    Keep Budget.spent in sync with expense Transactions.
    Handles:
      - created transaction (add amount to budget.spent)
      - updated transaction (apply delta or move between categories)
      - fallback (recalculate total for the category) if snapshot missing
    Only acts on expenses with a category.
    """
    # only handle expenses that have a category
    if instance.type != "expense" or instance.category_id is None:
        return

    with db_transaction.atomic():
        user = instance.user
        curr_amount = Decimal(instance.amount or 0)
        curr_category = instance.category            # Category instance
        curr_category_id = instance.category_id      # id for queries

        # Created expense -> increment (or create) budget.spent
        if created:
            budget, _ = Budget.objects.get_or_create(
                user=user,
                category=curr_category,
                defaults={"amount": Decimal("0.00"), "spent": Decimal("0.00")},
            )
            budget.spent = (budget.spent or Decimal("0.00")) + curr_amount
            budget.save(update_fields=["spent"])
            return

        # Update case -> compare with snapshot
        prev = getattr(instance, "_pre_save_snapshot", None)

        # If we don't have prev snapshot, recalc the total for the category (safe fallback)
        if prev is None:
            total = (
                Transaction.objects.filter(
                    user=user, category=curr_category_id, type="expense"
                ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
            )
            budget, _ = Budget.objects.get_or_create(
                user=user,
                category=curr_category,
                defaults={"amount": Decimal("0.00"), "spent": Decimal("0.00")},
            )
            budget.spent = Decimal(total)
            budget.save(update_fields=["spent"])
            return

        # We have prev snapshot -> compute delta and/or category move
        prev_amount = Decimal(prev.amount or 0)
        prev_category = prev.category  # Category instance (or None)

        # if category changed, remove prev_amount from old budget and add curr_amount to new budget
        if prev_category and prev_category.id != curr_category_id:
            # decrement old budget
            try:
                old_budget = Budget.objects.get(user=user, category=prev_category)
                old_budget.spent = (old_budget.spent or Decimal("0.00")) - prev_amount
                if old_budget.spent < 0:
                    old_budget.spent = Decimal("0.00")
                old_budget.save(update_fields=["spent"])
            except Budget.DoesNotExist:
                # no old budget to adjust
                pass

            # increment (or create) new budget
            new_budget, _ = Budget.objects.get_or_create(
                user=user,
                category=curr_category,
                defaults={"amount": Decimal("0.00"), "spent": Decimal("0.00")},
            )
            new_budget.spent = (new_budget.spent or Decimal("0.00")) + curr_amount
            new_budget.save(update_fields=["spent"])
            return

        # same category -> apply delta
        delta = curr_amount - prev_amount
        if delta != 0:
            budget, _ = Budget.objects.get_or_create(
                user=user,
                category=curr_category,
                defaults={"amount": Decimal("0.00"), "spent": Decimal("0.00")},
            )
            budget.spent = (budget.spent or Decimal("0.00")) + delta
            if budget.spent < 0:
                budget.spent = Decimal("0.00")
            budget.save(update_fields=["spent"])


@receiver(post_delete, sender=Transaction)
def transaction_post_delete(sender, instance, **kwargs):
    """
    When an expense is deleted, subtract its amount from the matching budget.
    """
    if instance.type != "expense" or instance.category_id is None:
        return

    with db_transaction.atomic():
        try:
            budget = Budget.objects.get(user=instance.user, category=instance.category)
            budget.spent = (budget.spent or Decimal("0.00")) - Decimal(instance.amount or 0)
            if budget.spent < 0:
                budget.spent = Decimal("0.00")
            budget.save(update_fields=["spent"])
        except Budget.DoesNotExist:
            pass
