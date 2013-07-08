
    fixtures = ['registration_tests.json', 'iss_testdata.json',
                'notification_emailtemplate_tests.json']

    multi_db = True

    def test_all_wizard_pages_load(self):
        pass

    def test_select_school_page_loads(self):
        pass

    def test_participation_level_page_loads(self):
        pass

    def test_contact_info_page_loads_for_participant(self):
        pass

    def test_contact_info_page_loads_for_respondent(self):
        pass

    def test_subscription_price_page_loads_for_participants(self):
        pass

    def test_subscription_price_page_does_not_load_for_respondent(self):
        pass

    def test_payment_options_page_loads_for_participant(self):
        pass

    def test_payment_options_page_does_not_load_for_respondent(self):
        pass

    def test_participant_finally_redirected_to_survey(self):
        pass

    def test_respondent_finally_redirected_to_survey(self):
        pass

    def test_two_emails_sent_for_respondent_registration(self):
        pass

    def test_participant_pay_later_sends_two_emails(self):
        # two emails sent out
        self.assertEqual(len(mail.outbox), 2)
        self.assertTrue(u'stars_test_liaison@aashe.org' in mail.outbox[0].to)
        self.assertTrue(u'stars_test_user@aashe.org' in mail.outbox[0].to)
        self.assertEqual(mail.outbox[1].to, [u'stars_test_exec@aashe.org'])

    def test_participant_pay_later_creates_institution(self):
        pass

    def test_participant_pay_later_creates_subscription(self):
        pass

    def test_participant_pay_later_does_not_create_subscription_payment(self):
        pass

    def test_participant_pay_later_creates_stars_account(self):
        pass

    def test_participant_pay_later_sets_institution_current_submission(self):
        self.assertIsNotNone(Institution.objects.all()[0].current_submission)
        pass

    def test_participant_pay_now_invalid_card_number_loads(self):
        # bogus card
        post_dict['payment-card_number'] = u'1212121212121'
        response = c.post(self.url, post_dict)
        self.assertEqual(response.status_code, 200)



    def test_participant_pay_later_sends_two_emails(self):
        # two emails sent out
        self.assertEqual(len(mail.outbox), 2)
        self.assertTrue(u'stars_test_liaison@aashe.org' in mail.outbox[0].to)
        self.assertTrue(u'stars_test_user@aashe.org' in mail.outbox[0].to)
        self.assertEqual(mail.outbox[1].to, [u'stars_test_exec@aashe.org'])

    def test_participant_pay_now_creates_institution(self):
        pass

    def test_participant_pay_now_creates_subscription(self):
        pass

    def test_participant_pay_now_creates_subscription_payment(self):
        pass

    def test_participant_pay_now_creates_stars_account(self):
        pass

    def test_participant_pay_now_sets_institution_current_submission(self):
        self.assertIsNotNone(Institution.objects.all()[0].current_submission)
        pass
