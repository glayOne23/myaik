# Don't use import all "*", as it can cause deadlock bugs

from .user import FormUserEdit, FormProfileEdit
from .profile import FormMyProfile, FormChangePassword, FormChangePasswordNew
from .groupdetails import FormGroupDetails
from .category import FormCategory
from .setting import FormSetting