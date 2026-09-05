from sentinel.correlation import detect_distributed_bruteforce


def event(ip, host, timestamp):
    return {"event": "ssh_login_failure", "source_ip": ip, "username": "x",
            "host": host, "timestamp": timestamp}


def test_detects_three_hosts_within_sixty_seconds():
    events = [event("10.0.0.9", f"victim{i}", f"2025-01-01T00:00:{i:02d}+00:00")
              for i in (0, 20, 40)]
    alerts = detect_distributed_bruteforce(events)
    assert alerts[-1]["mitre_technique"] == "T1110"
    assert alerts[-1]["host_count"] == 3


def test_does_not_alert_outside_window():
    events = [event("10.0.0.9", "victim1", "2025-01-01T00:00:00+00:00"),
              event("10.0.0.9", "victim2", "2025-01-01T00:00:20+00:00"),
              event("10.0.0.9", "victim3", "2025-01-01T00:01:21+00:00")]
    assert detect_distributed_bruteforce(events) == []
