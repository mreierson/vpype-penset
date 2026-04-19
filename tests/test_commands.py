"""Integration tests for vpype-penset commands."""

import vpype_cli

from vpype_penset.penset import Pen
from vpype_penset.pipeline import PENSET_METADATA_KEY


class TestPensetCommand:
    def test_penset_sets_metadata(self):
        doc = vpype_cli.execute("penset warm")
        assert doc is not None
        assert PENSET_METADATA_KEY in doc.metadata
        ps = doc.metadata[PENSET_METADATA_KEY]
        assert ps.name == "warm"

    def test_penset_with_hex_colors(self):
        doc = vpype_cli.execute('penset "#ff0000,#00ff00,#0000ff"')
        assert doc is not None
        ps = doc.metadata[PENSET_METADATA_KEY]
        assert len(ps.colors) == 3

    def test_penset_with_hex_and_width(self):
        doc = vpype_cli.execute('penset "#ff0000:0.7,#00ff00:0.5"')
        assert doc is not None
        ps = doc.metadata[PENSET_METADATA_KEY]
        assert len(ps.pens) == 2
        assert ps.pens[0].width == 0.7
        assert ps.pens[1].width == 0.5

    def test_penset_pens_are_pen_objects(self):
        doc = vpype_cli.execute("penset stabilo88")
        ps = doc.metadata[PENSET_METADATA_KEY]
        for pen in ps.pens:
            assert isinstance(pen, Pen)

    def test_penset_loads_toml(self, tmp_path):
        toml_file = tmp_path / "test_pens.toml"
        toml_file.write_text(
            "[penset]\n"
            'name = "test-set"\n'
            "\n"
            "[[penset.pens]]\n"
            'color = "#000000"\n'
            "width = 0.7\n"
            'name = "Black"\n'
            "\n"
            "[[penset.pens]]\n"
            'color = "#ff0000"\n'
            "width = 0.5\n"
            'name = "Red"\n'
        )
        doc = vpype_cli.execute(f'penset "{toml_file}"')
        assert doc is not None
        ps = doc.metadata[PENSET_METADATA_KEY]
        assert ps.name == "test-set"
        assert len(ps.pens) == 2
        assert ps.pens[0].width == 0.7

    def test_penset_toml_flows_to_colorize(self, tmp_path):
        toml_file = tmp_path / "flow.toml"
        toml_file.write_text(
            "[[penset.pens]]\n"
            'color = "#000000"\n'
            "width = 0.4\n"
            "\n"
            "[[penset.pens]]\n"
            'color = "#ff0000"\n'
            "width = 0.3\n"
        )
        doc = vpype_cli.execute(
            f'penset "{toml_file}" '
            "line --layer 1 0 0 10mm 10mm "
            "line --layer 2 0 0 20mm 20mm "
            "colorize"
        )
        assert doc is not None
        layers = sorted(doc.layers)
        assert len(layers) == 2
        assert doc[layers[0]].property("vp_pen_width") == 0.4
        assert doc[layers[1]].property("vp_pen_width") == 0.3


class TestColorizeCommand:
    def test_colorize_applies_colors(self):
        doc = vpype_cli.execute("penset rainbow line 0 0 10mm 10mm line 0 0 20mm 20mm colorize")
        assert doc is not None
        layers = sorted(doc.layers)
        assert len(layers) >= 1
        for lid in layers:
            color = doc[lid].property("vp_color")
            assert color is not None

    def test_colorize_sets_pen_width(self):
        doc = vpype_cli.execute("penset stabilo88 line 0 0 10mm 10mm line 0 0 20mm 20mm colorize")
        assert doc is not None
        layers = sorted(doc.layers)
        for lid in layers:
            width = doc[lid].property("vp_pen_width")
            assert width == 0.4

    def test_colorize_no_width_when_unspecified(self):
        doc = vpype_cli.execute("penset warm line 0 0 10mm 10mm colorize")
        assert doc is not None
        layers = sorted(doc.layers)
        for lid in layers:
            # warm pen set has no pen widths
            width = doc[lid].property("vp_pen_width")
            assert width is None

    def test_colorize_with_override(self):
        doc = vpype_cli.execute("line 0 0 10mm 10mm colorize --penset cool")
        assert doc is not None

    def test_colorize_reverse(self):
        doc = vpype_cli.execute(
            "penset warm line 0 0 10mm 10mm line 0 0 20mm 20mm colorize --reverse"
        )
        assert doc is not None


class TestPensetsCommand:
    def test_pensets_runs(self, capsys):
        doc = vpype_cli.execute("pensets")
        assert doc is not None
        captured = capsys.readouterr()
        assert "warm" in captured.out
        assert "stabilo88" in captured.out

    def test_pensets_lists_all(self, capsys):
        vpype_cli.execute("pensets")
        captured = capsys.readouterr()
        from vpype_penset.penset import PEN_SETS

        for name in PEN_SETS:
            assert name in captured.out


class TestPeninfoCommand:
    def test_peninfo_runs(self):
        doc = vpype_cli.execute("penset stabilo88 peninfo")
        assert doc is not None

    def test_peninfo_with_override(self):
        doc = vpype_cli.execute("peninfo --penset warm")
        assert doc is not None
