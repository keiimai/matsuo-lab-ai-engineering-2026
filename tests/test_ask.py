from app import ask


def test_main_reuses_chat_for_follow_up_questions(monkeypatch, capsys):
    class FakeResponse:
        def __init__(self, text):
            self.text = text
            self.usage_metadata = None

    class FakeChat:
        def __init__(self):
            self.questions = []

        def send_message(self, question):
            self.questions.append(question)
            return FakeResponse(f"回答: {question}")

    class FakeChats:
        def __init__(self):
            self.created = []

        def create(self, *, model):
            chat = FakeChat()
            self.created.append((model, chat))
            return chat

    class FakeClient:
        def __init__(self):
            self.chats = FakeChats()

    client = FakeClient()
    timestamps = iter([10.0, 11.25, 12.0, 14.0])
    monkeypatch.setattr(ask.genai, "Client", lambda *, api_key: client)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(ask, "perf_counter", lambda: next(timestamps))
    monkeypatch.setattr("sys.argv", ["app.ask", "最初の質問"])

    answers = iter(["続きの質問", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    ask.main()

    assert len(client.chats.created) == 1
    model, chat = client.chats.created[0]
    assert model == ask.MODEL
    assert chat.questions == ["最初の質問", "続きの質問"]
    output = capsys.readouterr().out
    assert "回答: 最初の質問" in output
    assert "回答: 続きの質問" in output
    assert "[応答時間] 1.25 秒" in output
    assert "[応答時間] 2.00 秒" in output
