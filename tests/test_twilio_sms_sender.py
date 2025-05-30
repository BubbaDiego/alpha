from notifications.twilio_sms_sender import TwilioSMSSender


class DummyClient:
    def __init__(self, *args, **kwargs):
        self.called = False

        class Messages:
            def __init__(self, outer):
                self.outer = outer

            def create(self, body=None, from_=None, to=None):
                self.outer.called = True
                return type("Msg", (), {"sid": "SM123"})()

        self.messages = Messages(self)


def test_twilio_sms_sender(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "sid")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "token")
    monkeypatch.setenv("TWILIO_FROM_PHONE", "+10000000000")

    monkeypatch.setattr("notifications.twilio_sms_sender.Client", DummyClient)

    sender = TwilioSMSSender()
    assert sender.send_sms("+15555555555", "test") is True
    assert isinstance(sender.client, DummyClient)
    assert sender.client.called is True


    sender = TwilioSMSSender()
    assert sender.send_sms("+15555555555", "test") is True

