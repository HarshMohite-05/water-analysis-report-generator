from report_engine.pagination import paginate


def test_small_table_single_page_with_remark():
    chunks, new_page = paginate(6)
    assert chunks == [(0, 6)] and new_page is False


def test_remark_moves_when_it_does_not_fit():
    chunks, new_page = paginate(14)  # 14 + 9 > 16
    assert chunks == [(0, 14)] and new_page is True


def test_multi_page_slices_cover_all_rows():
    chunks, _ = paginate(50)
    assert chunks[0] == (0, 16) and chunks[-1][1] == 50
    assert all(a < b for a, b in chunks)