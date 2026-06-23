def _walk(nodes):
    for n in nodes:
        yield n
        yield from _walk(n["children"])


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_tree_structure(client):
    res = client.get("/api/syllabus/tree")
    assert res.status_code == 200
    tree = res.json()

    # Two top-level stages: prelims + mains.
    titles = {n["title"] for n in tree}
    assert {"Prelims", "Mains"} <= titles

    all_nodes = list(_walk(tree))
    assert len(all_nodes) > 30  # rich tree

    # Every non-leaf has children; every leaf is marked is_leaf.
    for n in all_nodes:
        if n["children"]:
            assert n["is_leaf"] is False
        else:
            assert n["is_leaf"] is True


def test_tree_filter_by_exam(client):
    tree = client.get("/api/syllabus/tree?exam=mains").json()
    assert all(n["exam"] == "mains" for n in _walk(tree))


def test_subtree_by_root(client):
    full = client.get("/api/syllabus/tree").json()
    # Find a paper-level node to use as a root.
    paper = next(n for n in _walk(full) if n["level"] == "paper")
    sub = client.get(f"/api/syllabus/tree?root={paper['slug']}").json()
    assert len(sub) == 1
    assert sub[0]["slug"] == paper["slug"]


def test_node_detail_breadcrumb(client):
    full = client.get("/api/syllabus/tree").json()
    leaf = next(n for n in _walk(full) if n["is_leaf"] and n["has_content"])
    detail = client.get(f"/api/syllabus/node/{leaf['slug']}").json()
    assert detail["slug"] == leaf["slug"]
    assert detail["is_leaf"] is True
    assert len(detail["breadcrumb"]) >= 2
    assert detail["breadcrumb"][-1]["slug"] == leaf["slug"]


def test_leaf_content(client):
    full = client.get("/api/syllabus/tree").json()
    leaf = next(n for n in _walk(full) if n["is_leaf"] and n["has_content"])
    res = client.get(f"/api/content/{leaf['slug']}")
    assert res.status_code == 200
    body = res.json()
    assert body["has_content"] is True
    assert len(body["body_md"]) > 50
    assert len(body["sources"]) >= 1


def test_content_placeholder_for_empty_leaf(client):
    full = client.get("/api/syllabus/tree").json()
    leaf = next(n for n in _walk(full) if n["is_leaf"] and not n["has_content"])
    body = client.get(f"/api/content/{leaf['slug']}").json()
    assert body["has_content"] is False
    assert "coming soon" in body["body_md"].lower()


def test_evaluate_stub(client):
    ev = client.post(
        "/api/evaluate",
        json={"question": "Discuss DPSP.", "answer": "word " * 10, "word_limit": 250},
    )
    assert ev.status_code == 200
    assert ev.json()["word_count"] == 10
