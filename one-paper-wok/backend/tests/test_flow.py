from tests.conftest import auth_headers


def _wait_job(client, headers, job_id: str) -> dict:
    job = client.get(f"/jobs/{job_id}", headers=headers)
    assert job.status_code == 200, job.text
    body = job.json()
    assert body["stage"] == "done", body
    return body


def _cook_book(client, headers, jpeg_bytes, title="思考，快与慢"):
    created = client.post(
        "/books", json={"title": title, "author": "卡尼曼", "mode": "full"}, headers=headers
    )
    assert created.status_code == 201, created.text
    book_id = created.json()["id"]
    upload = client.post(
        f"/books/{book_id}/pages",
        headers=headers,
        files=[
            ("files", ("p1.jpg", jpeg_bytes, "image/jpeg")),
            ("files", ("p2.jpg", jpeg_bytes, "image/jpeg")),
        ],
    )
    assert upload.status_code == 200, upload.text
    cook = client.post(f"/books/{book_id}/cook", headers=headers)
    assert cook.status_code == 202, cook.text
    _wait_job(client, headers, cook.json()["id"])
    return book_id


def test_cook_produces_project_and_searchable_pdf(client, jpeg_bytes):
    headers = auth_headers(client)
    book_id = _cook_book(client, headers, jpeg_bytes)

    detail = client.get(f"/books/{book_id}", headers=headers)
    assert detail.json()["status"] == "done"
    assert detail.json()["page_count"] == 2
    assert detail.json()["has_project"] is True
    assert detail.json()["ebook"]["has_pdf"] is True

    project = client.get(f"/books/{book_id}/project", headers=headers)
    assert project.status_code == 200
    body = project.json()
    assert body["summary"]
    assert isinstance(body["key_insights"], list)
    assert body["chapter_outline"]

    page_text = client.get(f"/books/{book_id}/pages/0/text", headers=headers)
    assert page_text.status_code == 200
    needle = (page_text.json()["text"] or "的")[:2]
    search = client.get(f"/books/{book_id}/search", params={"q": needle}, headers=headers)
    assert search.status_code == 200
    assert search.json()["hits"]

    pdf = client.get(f"/books/{book_id}/ebook.pdf", headers=headers)
    assert pdf.status_code == 200
    assert pdf.content[:4] == b"%PDF"


def test_epub_export(client, jpeg_bytes):
    headers = auth_headers(client)
    book_id = _cook_book(client, headers, jpeg_bytes, title="纳瓦尔宝典")
    job = client.post(f"/books/{book_id}/export/epub", headers=headers)
    assert job.status_code == 202
    _wait_job(client, headers, job.json()["id"])
    epub = client.get(f"/books/{book_id}/ebook.epub", headers=headers)
    assert epub.status_code == 200
    assert epub.content[:2] == b"PK"


def test_translate_is_cached(client, jpeg_bytes):
    headers = auth_headers(client)
    book_id = _cook_book(client, headers, jpeg_bytes)
    first = client.post(
        f"/books/{book_id}/translate",
        json={"page_index": 0, "target_lang": "en"},
        headers=headers,
    )
    assert first.status_code == 200
    segs = first.json()["segments"]
    assert segs
    assert segs[0]["text"].startswith("[en]")
    second = client.post(
        f"/books/{book_id}/translate",
        json={"page_index": 0, "target_lang": "en"},
        headers=headers,
    )
    assert second.json()["segments"][0]["text"] == segs[0]["text"]


def test_recook_updates_project_version(client, jpeg_bytes):
    headers = auth_headers(client)
    book_id = _cook_book(client, headers, jpeg_bytes)
    before = client.get(f"/books/{book_id}/project", headers=headers).json()["version"]

    typed = client.post(
        f"/books/{book_id}/annotations/typed",
        json={"text": "第一个价格就是锚点", "page_index": 0, "client_op_id": "op-1"},
        headers=headers,
    )
    assert typed.status_code == 201
    idem = client.post(
        f"/books/{book_id}/annotations/typed",
        json={"text": "重复提交", "page_index": 0, "client_op_id": "op-1"},
        headers=headers,
    )
    assert idem.json()["id"] == typed.json()["id"]

    recook = client.post(f"/books/{book_id}/recook", headers=headers)
    assert recook.status_code == 202
    _wait_job(client, headers, recook.json()["id"])

    after = client.get(f"/books/{book_id}/project", headers=headers).json()
    assert after["version"] == before + 1
    assert after["personal_insights"]
    versions = client.get(f"/books/{book_id}/project/versions", headers=headers)
    assert versions.status_code == 200
    assert versions.json()

    notes = client.get(f"/books/{book_id}/annotations", headers=headers)
    assert notes.json()[0]["status"] == "refined"


def test_scan_annotation_and_correct(client, jpeg_bytes):
    headers = auth_headers(client)
    book_id = _cook_book(client, headers, jpeg_bytes)
    upload = client.post(
        f"/books/{book_id}/annotations",
        headers=headers,
        files=[("files", ("note.jpg", jpeg_bytes, "image/jpeg"))],
        data={"page_index": "1"},
    )
    assert upload.status_code == 201
    ann_id = upload.json()[0]["id"]
    patch = client.patch(
        f"/books/{book_id}/annotations/{ann_id}",
        json={"handwritten_text": "手动修正后的批注"},
        headers=headers,
    )
    assert patch.status_code == 200
    assert patch.json()["handwritten_text"] == "手动修正后的批注"
    img = client.get(f"/books/{book_id}/annotations/{ann_id}/image", headers=headers)
    assert img.status_code == 200


def test_sync_includes_soft_deletes(client, jpeg_bytes):
    headers = auth_headers(client)
    book_id = _cook_book(client, headers, jpeg_bytes)
    full = client.get("/sync", headers=headers)
    assert full.status_code == 200
    assert any(b["id"] == book_id for b in full.json()["books"])
    server_time = full.json()["server_time"]

    client.delete(f"/books/{book_id}", headers=headers)
    listed = client.get("/books", headers=headers)
    assert listed.json() == []

    incremental = client.get("/sync", params={"since": server_time}, headers=headers)
    deleted = [b for b in incremental.json()["books"] if b["id"] == book_id]
    assert deleted
    assert deleted[0]["deleted_at"] is not None


def test_user_isolation(client, jpeg_bytes):
    a = auth_headers(client, "a@example.com")
    b = auth_headers(client, "b@example.com")
    book_id = _cook_book(client, a, jpeg_bytes)
    assert client.get(f"/books/{book_id}", headers=b).status_code == 404
    assert client.get("/books", headers=b).json() == []
