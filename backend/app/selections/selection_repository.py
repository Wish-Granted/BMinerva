from abc import ABC, abstractmethod

class SelectionRepository(ABC):
    def get_selection(username) -> dict:
        """Returns all selections for a given user"""
        raise NotImplementedError

    def get_sort(username):
        """Returns sort preferences for a user"""
        raise NotImplementedError

    def replace_selection(username, student_ids, called_ids, sort):
        """Replace the user's whole selection in one transaction.
        Keeps the original added_at for students who were already selected."""
        raise NotImplementedError