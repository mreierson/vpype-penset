"""Tests for pen set data model, pen model, and predefined pen sets."""

import click
import pytest
import vpype as vp

from vpype_penset.penset import (
    Pen,
    PenSet,
    PenSetParamType,
    _parse_hex_color,
    _parse_pen_spec,
    export_penset,
    load_penset,
)


class TestPen:
    def test_basic_construction(self):
        pen = Pen(color=vp.Color(255, 0, 0))
        assert pen.color.red == 255
        assert pen.width is None
        assert pen.name is None

    def test_full_construction(self):
        pen = Pen(color=vp.Color(0, 0, 255), width=0.7, name="Blue G-2")
        assert pen.color.blue == 255
        assert pen.width == 0.7
        assert pen.name == "Blue G-2"

    def test_frozen(self):
        pen = Pen(color=vp.Color(0, 0, 0))
        with pytest.raises(AttributeError):
            pen.width = 1.0

    def test_equality(self):
        a = Pen(color=vp.Color(255, 0, 0), width=0.5)
        b = Pen(color=vp.Color(255, 0, 0), width=0.5)
        assert a == b

    def test_inequality_different_width(self):
        a = Pen(color=vp.Color(255, 0, 0), width=0.5)
        b = Pen(color=vp.Color(255, 0, 0), width=0.7)
        assert a != b


class TestPenSet:
    def test_sample_pens_exact_count(self):
        ps = PenSet("test", (Pen(color=vp.Color(255, 0, 0)), Pen(color=vp.Color(0, 255, 0))))
        pens = ps.sample_pens(2)
        assert len(pens) == 2
        assert pens[0].color.red == 255
        assert pens[1].color.green == 255

    def test_sample_pens_fewer_than_available(self):
        ps = PenSet(
            "test",
            (
                Pen(color=vp.Color(255, 0, 0)),
                Pen(color=vp.Color(0, 255, 0)),
                Pen(color=vp.Color(0, 0, 255)),
            ),
        )
        pens = ps.sample_pens(2)
        assert len(pens) == 2

    def test_sample_pens_more_than_available_cycles(self):
        ps = PenSet("test", (Pen(color=vp.Color(255, 0, 0)), Pen(color=vp.Color(0, 255, 0))))
        pens = ps.sample_pens(5)
        assert len(pens) == 5
        assert pens[0].color.red == 255  # index 0
        assert pens[2].color.red == 255  # index 2 wraps to 0

    def test_sample_pens_zero(self):
        ps = PenSet("test", (Pen(color=vp.Color(255, 0, 0)),))
        assert ps.sample_pens(0) == []

    def test_sample_colors_returns_colors(self):
        ps = PenSet("test", (Pen(color=vp.Color(255, 0, 0), width=0.5),))
        colors = ps.sample_colors(1)
        assert len(colors) == 1
        assert isinstance(colors[0], vp.Color)
        assert colors[0].red == 255

    def test_colors_property(self):
        ps = PenSet(
            "test",
            (Pen(color=vp.Color(255, 0, 0)), Pen(color=vp.Color(0, 255, 0))),
        )
        colors = ps.colors
        assert len(colors) == 2
        assert colors[0].red == 255
        assert colors[1].green == 255

    def test_auto_wrap_bare_colors(self):
        """PenSet should auto-wrap bare vp.Color objects in Pen."""
        ps = PenSet("test", (vp.Color(255, 0, 0), vp.Color(0, 255, 0)))
        assert len(ps.pens) == 2
        assert isinstance(ps.pens[0], Pen)
        assert ps.pens[0].color.red == 255

    def test_from_colors_factory(self):
        ps = PenSet.from_colors("test", (vp.Color(255, 0, 0),))
        assert len(ps.pens) == 1
        assert isinstance(ps.pens[0], Pen)
        assert ps.pens[0].color.red == 255

    def test_len(self):
        ps = PenSet("test", (Pen(color=vp.Color(0, 0, 0)), Pen(color=vp.Color(255, 255, 255))))
        assert len(ps) == 2

    def test_frozen(self):
        ps = PenSet("test", (Pen(color=vp.Color(0, 0, 0)),))
        with pytest.raises(AttributeError):
            ps.name = "other"

    def test_sample_pens_preserves_width(self):
        ps = PenSet("test", (Pen(color=vp.Color(0, 0, 0), width=0.7),))
        pens = ps.sample_pens(3)
        assert all(p.width == 0.7 for p in pens)


class TestInterpolate:
    """Tests for PenSet.interpolate()."""

    @pytest.fixture()
    def six_pen_set(self) -> PenSet:
        """A 6-pen gradient from black to white for predictable interpolation."""
        return PenSet(
            "grad",
            tuple(
                Pen(color=vp.Color(v, v, v))
                for v in (0, 50, 100, 150, 200, 250)
            ),
        )

    def test_interpolate_same_count(self, six_pen_set: PenSet):
        result = six_pen_set.interpolate(6)
        assert isinstance(result, PenSet)
        assert len(result) == 6
        # Colors should match the originals exactly.
        for orig, interp in zip(six_pen_set.pens, result.pens, strict=True):
            assert interp.color.red == orig.color.red
            assert interp.color.green == orig.color.green
            assert interp.color.blue == orig.color.blue

    def test_interpolate_expand(self, six_pen_set: PenSet):
        result = six_pen_set.interpolate(12)
        assert isinstance(result, PenSet)
        assert len(result) == 12
        # First and last colors must match the source endpoints.
        assert result.pens[0].color.red == 0
        assert result.pens[-1].color.red == 250
        # All colors should be valid vp.Color instances.
        for pen in result.pens:
            assert isinstance(pen.color, vp.Color)

    def test_interpolate_contract(self, six_pen_set: PenSet):
        result = six_pen_set.interpolate(3)
        assert isinstance(result, PenSet)
        assert len(result) == 3
        # First and last should match endpoints.
        assert result.pens[0].color.red == 0
        assert result.pens[-1].color.red == 250

    def test_interpolate_single(self, six_pen_set: PenSet):
        result = six_pen_set.interpolate(1)
        assert isinstance(result, PenSet)
        assert len(result) == 1
        # Should return the first color.
        assert result.pens[0].color.red == 0

    def test_interpolate_two(self, six_pen_set: PenSet):
        result = six_pen_set.interpolate(2)
        assert isinstance(result, PenSet)
        assert len(result) == 2
        # First and last color of the source.
        assert result.pens[0].color.red == 0
        assert result.pens[1].color.red == 250

    def test_interpolate_names_and_width(self, six_pen_set: PenSet):
        result = six_pen_set.interpolate(4)
        for i, pen in enumerate(result.pens):
            assert pen.name == f"interp-{i}"
            assert pen.width is None

    def test_interpolate_returns_penset(self, six_pen_set: PenSet):
        result = six_pen_set.interpolate(5)
        assert isinstance(result, PenSet)
        assert result.name == "grad-interp"


class TestParseHexColor:
    def test_full_hex(self):
        c = _parse_hex_color("#ff0000")
        assert c.red == 255 and c.green == 0 and c.blue == 0

    def test_short_hex(self):
        c = _parse_hex_color("#f00")
        assert c.red == 255 and c.green == 0 and c.blue == 0

    def test_no_hash(self):
        c = _parse_hex_color("00ff00")
        assert c.green == 255

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            _parse_hex_color("#xyz")


class TestParsePenSpec:
    def test_color_only(self):
        pen = _parse_pen_spec("#ff0000")
        assert pen.color.red == 255
        assert pen.width is None

    def test_color_with_width(self):
        pen = _parse_pen_spec("#ff0000:0.7")
        assert pen.color.red == 255
        assert pen.width == 0.7

    def test_invalid_width(self):
        with pytest.raises(ValueError, match="Invalid pen width"):
            _parse_pen_spec("#ff0000:abc")

    def test_too_many_colons(self):
        with pytest.raises(ValueError, match="Invalid pen spec"):
            _parse_pen_spec("#ff0000:0.7:extra")


class TestPenSetParamType:
    def test_named_penset(self):
        pt = PenSetParamType()
        result = pt.convert("warm", None, None)
        assert result.name == "warm"

    def test_hex_colors(self):
        pt = PenSetParamType()
        result = pt.convert("#ff0000,#00ff00", None, None)
        assert result.name == "custom"
        assert len(result.colors) == 2

    def test_hex_colors_with_width(self):
        pt = PenSetParamType()
        result = pt.convert("#ff0000:0.7,#00ff00:0.5", None, None)
        assert result.name == "custom"
        assert len(result.pens) == 2
        assert result.pens[0].width == 0.7
        assert result.pens[1].width == 0.5

    def test_mixed_width_and_no_width(self):
        pt = PenSetParamType()
        result = pt.convert("#ff0000:0.7,#00ff00", None, None)
        assert result.pens[0].width == 0.7
        assert result.pens[1].width is None

    def test_passthrough_penset_object(self):
        pt = PenSetParamType()
        ps = PenSet("test", (Pen(color=vp.Color(0, 0, 0)),))
        assert pt.convert(ps, None, None) is ps

    def test_invalid_name_fails(self):
        pt = PenSetParamType()
        with pytest.raises(click.exceptions.BadParameter):
            pt.convert("nonexistent", None, None)

    def test_toml_file(self, tmp_path):
        toml_file = tmp_path / "pens.toml"
        toml_file.write_text(
            '[penset]\nname = "from-param"\n\n[[penset.pens]]\ncolor = "#ff0000"\nwidth = 0.5\n'
        )
        pt = PenSetParamType()
        result = pt.convert(str(toml_file), None, None)
        assert result.name == "from-param"
        assert len(result.pens) == 1
        assert result.pens[0].width == 0.5


class TestLoadPenset:
    def test_load_basic(self, tmp_path):
        toml_file = tmp_path / "pens.toml"
        toml_file.write_text(
            "[penset]\n"
            'name = "test-pens"\n'
            "\n"
            "[[penset.pens]]\n"
            'color = "#000000"\n'
            "width = 0.7\n"
            'name = "Black"\n'
            "\n"
            "[[penset.pens]]\n"
            'color = "#0000ff"\n'
            "width = 0.5\n"
            'name = "Blue"\n'
        )
        ps = load_penset(toml_file)
        assert ps.name == "test-pens"
        assert len(ps.pens) == 2
        assert ps.pens[0].width == 0.7
        assert ps.pens[0].name == "Black"
        assert ps.pens[1].color.blue == 255

    def test_load_minimal(self, tmp_path):
        toml_file = tmp_path / "minimal.toml"
        toml_file.write_text('[[penset.pens]]\ncolor = "#ff0000"\n')
        ps = load_penset(toml_file)
        assert ps.name == "minimal"  # derives from filename
        assert len(ps.pens) == 1
        assert ps.pens[0].width is None

    def test_load_no_pens_raises(self, tmp_path):
        toml_file = tmp_path / "empty.toml"
        toml_file.write_text('[penset]\nname = "empty"\n')
        with pytest.raises(ValueError, match="No pens defined"):
            load_penset(toml_file)

    def test_load_missing_color_raises(self, tmp_path):
        toml_file = tmp_path / "bad.toml"
        toml_file.write_text('[[penset.pens]]\nwidth = 0.7\nname = "no-color"\n')
        with pytest.raises(ValueError, match="missing 'color'"):
            load_penset(toml_file)


class TestExportPenset:
    def test_export_roundtrip(self, tmp_path):
        """Export a pen set, then load it back and verify it matches."""
        ps = PenSet(
            "roundtrip",
            (
                Pen(color=vp.Color(255, 0, 0), width=0.7, name="Red"),
                Pen(color=vp.Color(0, 128, 255), width=0.3, name="Blue"),
                Pen(color=vp.Color(0, 200, 0)),
            ),
        )
        toml_file = tmp_path / "exported.toml"
        export_penset(ps, toml_file)

        loaded = load_penset(toml_file)
        assert loaded.name == "roundtrip"
        assert len(loaded.pens) == 3
        assert loaded.pens[0].color.red == 255
        assert loaded.pens[0].width == 0.7
        assert loaded.pens[0].name == "Red"
        assert loaded.pens[1].color.blue == 255
        assert loaded.pens[1].width == 0.3
        assert loaded.pens[2].width is None
        assert loaded.pens[2].name is None

    def test_export_builtin_roundtrip(self, tmp_path):
        """Export a built-in pen set and reload it."""
        from vpype_penset.penset import PEN_SETS

        ps = PEN_SETS["stabilo88"]
        toml_file = tmp_path / "stabilo88.toml"
        export_penset(ps, toml_file)

        loaded = load_penset(toml_file)
        assert loaded.name == ps.name
        assert len(loaded.pens) == len(ps.pens)
        for orig, exported in zip(ps.pens, loaded.pens, strict=True):
            assert orig.color.red == exported.color.red
            assert orig.color.green == exported.color.green
            assert orig.color.blue == exported.color.blue
            assert orig.width == exported.width
            assert orig.name == exported.name
