from musa_video.project import create_project

def test_project_scaffold(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    project = create_project("Test topic", scenes=3)
    assert (project / "brief.json").exists()
    assert (project / "storyboard.json").exists()
    assert (project / "prompts.md").exists()
