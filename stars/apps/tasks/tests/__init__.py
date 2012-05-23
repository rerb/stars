from notify_tests import NotificationTest
import test_add_months
from renew_notify_test import RenewNotifyTest
from subscription_monitor_test import SubscriptionMonitorTest

__test__ = {
    'notify': NotificationTest,
    'add_months': test_add_months,
    'renew_notify_test': RenewNotifyTest,
    'subscription_monitor_test': SubscriptionMonitorTest,
}
