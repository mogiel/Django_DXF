# Copyright (c) 2021-2022, Mogielski Mateusz - KONEC
# Copyright (c) 2011-2022, Manfred Moitzi - EZDXF
import math
import re
from typing import Literal
import ezdxf
import ezdxf.math
from ezdxf import zoom
from ezdxf.enums import TextEntityAlignment

from calc.app.LANG.LANG_PL import LANG_PL
from calc.app.LANG.LANG_DE import LANG_DE
from calc.app.LANG.LANG_ENG import LANG_ENG


def point_position(x0: float, y0: float, distance: float, theta: float = 60) -> tuple[float, float]:
    """
    theta zgodna z ruchem wskazowek zegara. godzina 12:00 to 0st, 3:00 to 90st, 6:00 to 180st, 9:00 to 270st
    """
    theta_rad = math.pi / 2 - math.radians(theta)
    return x0 + distance * math.cos(theta_rad), y0 + distance * math.sin(theta_rad)


def tuple_dest(tuple_start: tuple[float, float], width: float = 0, height: float = 0) -> tuple[float, float]:
    return tuple_start[0] + width, tuple_start[1] + height


def spacing_between_bars(diameter: float, diameter_aggregate: float = 16) -> float:
    return math.ceil(max(diameter, 20, diameter_aggregate + 5)) + diameter


class DxfElement:
    def __init__(self,
                 beam_span: float,
                 beam_height: float,
                 beam_width: float,
                 width_support_left: int,
                 width_support_right: int,
                 diameter_main_top: int,
                 quantity_main_top: int,
                 steel_grade_main_top: str,
                 diameter_main_bottom: int,
                 quantity_main_bottom: int,
                 steel_grade_main_bottom: str,
                 diameter_stirrup: int,
                 steel_grade_stirrup: str,
                 cover_view_left: int,
                 cover_view_right: int,
                 cover_bottom: int,
                 cover_top: int,
                 cover_left: int,
                 cover_right: int,
                 first_row_stirrup_range_left: int,
                 first_row_stirrup_range_right: int,
                 first_row_stirrup_spacing_left: int,
                 first_row_stirrup_spacing_right: int,
                 secondary_stirrup_spacing: int,
                 number_of_elements: int = 1,
                 name: str = "Belka",
                 dxfversion: str = 'R2018',
                 start_point_x: float = 0,
                 start_point_y: float = 0,
                 language: str = 'pl') -> object:

        self.first_row_stirrup_spacing_right = self._is_valid_value(first_row_stirrup_spacing_right, 0, 400)
        self.first_row_stirrup_spacing_left = self._is_valid_value(first_row_stirrup_spacing_left, 0, 400)
        self.first_row_stirrup_range_right = self._is_valid_value(first_row_stirrup_range_right, 0, 15000)
        self.first_row_stirrup_range_left = self._is_valid_value(first_row_stirrup_range_left, 0, 15000)
        self.name = self._is_valid_path_name(name)
        self.number_of_elements = self._is_valid_value(number_of_elements, 1, 1000)
        self.cover_right = self._is_valid_value(cover_right, 5, 100)
        self.cover_left = self._is_valid_value(cover_left, 5, 100)
        self.beam_width = self._is_valid_value(beam_width, 100, 1000)
        self.cover_top = self._is_valid_value(cover_top, 5, 100)
        self.cover_bottom = self._is_valid_value(cover_bottom, 5, 100)
        self.cover_view_right = self._is_valid_value(cover_view_right, 5, 100)
        self.cover_view_left = self._is_valid_value(cover_view_left, 5, 100)
        self.diameter_main_bottom = self._is_valid_value(diameter_main_bottom, 1, 100)
        self.quantity_main_top = self._is_valid_value(quantity_main_top, 1, 40)
        self.steel_grade_main_top = self._is_valid_path_name(steel_grade_main_top)
        self.diameter_main_top = self._is_valid_value(diameter_main_top, 1, 100)
        self.quantity_main_bottom = self._is_valid_value(quantity_main_bottom, 1, 40)
        self.steel_grade_main_bottom = self._is_valid_path_name(steel_grade_main_bottom)
        self.diameter_stirrup = self._is_valid_value(diameter_stirrup, 1, 100)
        self.steel_grade_stirrup = self._is_valid_path_name(steel_grade_stirrup)
        self.start_point_y = start_point_y
        self.start_point_x = start_point_x
        self.width_support_right = self._is_valid_value(width_support_right, 50, 1000)
        self.width_support_left = self._is_valid_value(width_support_left, 50, 1000)
        self.beam_span = self._is_valid_value_beam(beam_span, first_row_stirrup_range_left,
                                                   first_row_stirrup_range_right, 300, 15000)
        self.beam_height = self._is_valid_value(beam_height, 100, 1500)
        self.language = self._is_valid_path_name(language)

        self.secondary_stirrup_spacing = math.floor(
            min(0.75 * self.beam_height * 0.9, self._is_valid_value(secondary_stirrup_spacing, 0, 400)) / 5) * 5
        self.dimension_points = [0.0, float(self.beam_span)]
        self.number_of_stirrups_of_the_second_row = None

        self.counter = None
        self.bar = None
        self.stirrup = None
        self.hatch = None
        self.dimension = None
        self.hidden = None
        self.dim_name = None
        self.dim_name_bar = None
        self.text = None
        self.steel_bill = []
        self.count_stirrups = 0
        self.position = {}

        self.dxfversion = dxfversion
        self.language_choice()
        self.drawing = ezdxf.new(dxfversion=self.dxfversion, setup=["linetypes"])
        self.initial_drawing()
        self.layer_element()
        self._start_points(start_y=-2*self.beam_height)
        self.msp = self.drawing.modelspace()
        self.beam_outline()
        self.view_top_bar(quantity_bar=int(self.quantity_main_top), steel_grade=self.steel_grade_main_top)
        self.view_top_bar(quantity_bar=int(self.quantity_main_top), steel_grade=self.steel_grade_main_top, dimension=True)
        self.view_bottom_bar(quantity_bar=int(self.quantity_main_bottom), steel_grade=self.steel_grade_main_bottom)
        self.view_bottom_bar(quantity_bar=int(self.quantity_main_bottom), steel_grade=self.steel_grade_main_bottom, dimension=True)
        self._secondary_stirrup_spacing_min()
        self.layout_new()
        self.stirrup_spacing()
        self.dimension_main()
        self.dimension_stirrup()
        self.beam_section_rectangular()
        self.view_stirrups_type_2()
        self.create_table(steel_bill=self.steel_bill)
        self.generate_block()
        # self.save()

    @staticmethod
    def _is_valid_value(value: float or int, min_value: float = 0, max_value: float = 99999):
        if not isinstance(value, (int, float)) or value < min_value or value > max_value:
            raise ValueError(f"{value} max is {max_value}[mm]")
        return value

    @staticmethod
    def _is_valid_value_beam(value: float, range_left: float, range_right: float, min_value: float = 0,
                             max_value: float = 99999) -> float or ValueError:
        if not isinstance(value, (int, float)) or value <= min_value or value > max_value or value - range_left - range_right < 0:
            raise ValueError(f"{value} max is {max_value}[mm]")
        return value

    @staticmethod
    def _is_valid_path_name(name: str) -> str or ValueError:
        """todo: poprawić regex, bo wywala błąd"""
        # regex = "^(?:[^/]*(?:/(?:/[^/]*/?)?)?([^?]+)(?:\??.+)?)$"
        regex = "/\\:*?\"<>|"
        if not re.match(regex, name) or name.__len__() > 20:
            raise ValueError("name is not regular expression for os")
        return name

    @staticmethod
    def bar_bending(diameter: float) -> float:
        """Obliczanie wygięcia pręta związanego ze średnicą pręta"""
        if diameter <= 16:
            return diameter * 2.5
        else:
            return diameter * 4.0

    @staticmethod
    def mass_1m_bar(diameter: float, mass: float = 7850) -> float:
        return round(mass * math.pi * ((diameter / 2) / 1000) ** 2, 3)

    def _secondary_stirrup_spacing_min(self) -> float:
        self.secondary_stirrup_spacing = math.floor(
            min(self.secondary_stirrup_spacing, 400, int(self.beam_height * 0.75)) / 5) * 5
        return self.secondary_stirrup_spacing

    def initial_drawing(self, LTSCALE: int = 50, INSUNITS: int = 4, MEASUREMENT: int = 1):
        """
        Inicjalizacja pliku rysunku cad
        LTSCALE - skala rysunku powizana z liniami, default=50
        INSUNITS - jednostki rysunkowe, default=4 (mm)
        """
        self.drawing.header['$LTSCALE'] = LTSCALE
        self.drawing.header['$INSUNITS'] = INSUNITS
        self.drawing.header['$MEASUREMENT'] = MEASUREMENT
        return self.drawing

    def language_choice(self):
        global LANG
        if self.language == 'pl':
            LANG = LANG_PL
        elif self.language == 'eng':
            LANG = LANG_ENG
        elif self.language == 'de':
            LANG = LANG_DE
        else:
            LANG = LANG_ENG

    def layer_element(self,
                      counter: str = 'KONEC-Obrys', color_counter: int = 3,
                      bar: str = 'KONEC-Prety', color_bar: int = 1,
                      stirrup: str = 'KONEC-Strzemiona', color_stirrup: int = 6,
                      hatch: str = 'KONEC-Kreskowanie', color_hatch: int = 7,
                      dimension: str = 'KONEC-Wymiary', color_dimension: int = 4,
                      hidden: str = 'KONEC-Przerywana', color_hidden: int = 8,
                      dim_name: str = 'KONEC_1_20', dim_scale: int = 20,
                      dim_name_bar: str = 'KONEC_BAR_1_20',
                      text: str = 'KONEC-Tekst', font_text: str = 'Arial.ttf'):
        """Tworzenie warstw, styli teksty i wymiarowania"""
        self.counter = counter
        self.bar = bar
        self.stirrup = stirrup
        self.hatch = hatch
        self.dimension = dimension
        self.hidden = hidden
        self.dim_name = dim_name
        self.dim_name_bar = dim_name_bar
        self.text = text

        self.drawing.layers.new(self.counter, dxfattribs={'color': color_counter})
        self.drawing.layers.new(bar, dxfattribs={'color': color_bar})
        self.drawing.layers.new(stirrup, dxfattribs={'color': color_stirrup})
        self.drawing.layers.new(hatch, dxfattribs={'color': color_hatch})
        self.drawing.layers.new(dimension, dxfattribs={'color': color_dimension})
        self.drawing.layers.new(hidden, dxfattribs={'color': color_hidden, 'linetype': 'DASHED'})
        self.drawing.styles.new(text, dxfattribs={'font': font_text})
        self.drawing.dimstyles.new(dim_name,
                                   dxfattribs={'dimjust': 0, 'dimscale': dim_scale, 'dimblk': 'OBLIQUE',
                                               'dimtxsty': text, 'dimtad': 1})
        self.drawing.dimstyles.new(dim_name_bar,
                                   dxfattribs={'dimjust': 0, 'dimscale': dim_scale, 'dimblk': 'NONE', 'dimtxsty': text,
                                               'dimtad': 1,
                                               'dimse1': 1, 'dimse2': 1, 'dimsd1': 1, 'dimsd2': 1, 'dimdle': 0})

        # In this place must create all blocks
        self._create_block_reinforcement_description()
        self._create_block_marker_left()
        self._create_block_marker_section()

    def _start_points(self, start_x: float = None, start_y: float = None):
        if start_x is None:
            start_x = self.start_point_x
        if start_y is None:
            start_y = self.start_point_y

        beam = self.width_support_left + self.beam_span + self.width_support_right

        # main beam
        self.position['main_beam'] = (start_x, start_y)
        # top bar dimension
        self.position['main_bar_top'] = (start_x, start_y - self.beam_height - 800)
        # bottom bar dimension
        self.position['main_bar_bottom'] = (start_x, start_y - self.beam_height - 950)
        # section
        self.position['section'] = (start_x + beam + 500, start_y)
        # stirrup
        self.position['stirrup'] = (start_x + beam + 500 + self.beam_width + 400, start_y)
        # bending_schedule
        self.position['bending_schedule'] = (start_x + beam + 300, start_y - 300)

    def save(self, filepath):
        """Zapisywanie do pliku"""
        zoom.extents(self.msp, factor=1.1)
        self.drawing.saveas(filepath)

    def bar_bulge(self, diameter):
        """funkcja potrzebna aby wyliczyć promień łuku dla wyoblenia"""
        bulge = self.bar_bending(diameter)
        math_bulge = ezdxf.math.arc_to_bulge((bulge, 0), math.pi, math.pi / 2, bulge)
        return -1 / math_bulge[2]

    def beam_outline(self):
        """generowanie obrysu belki"""
        start_point_x, start_point_y = self.position['main_beam']
        points = [(start_point_x, start_point_y),
                  (start_point_x + self.width_support_left, start_point_y),
                  ((start_point_x + self.width_support_left + self.beam_span), start_point_y),
                  ((start_point_x + self.width_support_left + self.beam_span + self.width_support_right),
                   start_point_y),
                  ((start_point_x + self.width_support_left + self.beam_span + self.width_support_right),
                   start_point_y + self.beam_height),
                  (start_point_x, start_point_y + self.beam_height)]
        self.msp.add_lwpolyline(points, dxfattribs={'closed': True, 'layer': self.counter})

        self.supports(start_point_x, start_point_x + self.width_support_left)
        self.supports(start_point_x + self.width_support_left + self.beam_span,
                      start_point_x + self.width_support_left + self.beam_span + self.width_support_right)

        self.generate_marker_section(
            (start_point_x + self.width_support_left + self.beam_span / 2, start_point_y + self.beam_height + 300), 'a')
        self.generate_marker_section(
            (start_point_x + self.width_support_left + self.beam_span / 2, start_point_y - 500), 'a')

    def length_bar(self, points: list, diameter: float, angle: int = 90) -> float:
        """angle jest to kąt pod jakim zmieniają się proste"""
        arc_radius = self.bar_bending(diameter)
        total_length_bar = 0
        for i in range(len(points) - 1):
            if len(points[i]) == 5:
                total_length_bar += 2 * (angle / 360) * math.pi * arc_radius
                continue
            total_length_bar += ((points[i][0] - points[i + 1][0]) ** 2 + (points[i][1] - points[i + 1][1]) ** 2) ** 0.5
        return round(total_length_bar)

    def list_bar(self, points: tuple[float, float], diameter: float = None, quantity_bar: int = None,
                 length: float = None, steel_grade: str = None,
                 name: str = None):
        self.steel_bill = [dict(t) for t in {tuple(d.items()) for d in self.steel_bill}]

        bar = {
            'name_element': self.name if name is None else self._is_valid_path_name(name),
            'number': len(self.steel_bill) + 1,
            'diameter': diameter,
            'quantity_bar': quantity_bar,
            'length': length,
            'steel_grade': steel_grade,
            'points_generate': points,
        }
        # todo: można dodać sortowanie po 'name_element' potem po 'number'
        self.steel_bill.append(bar)
        self.steel_bill.sort(key=(lambda x: x['number']))

    def view_top_bar(self, quantity_bar: int, steel_grade: str, dimension: bool = False, start_point_x: float = None,
                     start_point_y: float = None):
        """generowanie pręta górnego"""

        if start_point_x is None:
            start_point_x = self.position['main_bar_top'][0] if dimension else self.position['main_beam'][0]
        if start_point_y is None:
            start_point_y = self.position['main_bar_top'][1] if dimension else self.position['main_beam'][1]

        bugle = self.bar_bulge(self.diameter_main_top)
        bending = self.bar_bending(self.diameter_main_top)
        points = [((start_point_x + self.cover_view_left + 0.5 * self.diameter_main_top),
                   start_point_y + self.cover_bottom, self.diameter_main_top,
                   self.diameter_main_top),
                  ((start_point_x + self.cover_view_left + 0.5 * self.diameter_main_top),
                   (
                           start_point_y + self.beam_height - self.cover_top - self.diameter_stirrup - 0.5 * self.diameter_main_top - bending),
                   self.diameter_main_top, self.diameter_main_top, bugle),
                  ((start_point_x + self.cover_view_left + 0.5 * self.diameter_main_top + bending),
                   (
                           start_point_y + self.beam_height - self.cover_top - self.diameter_stirrup - 0.5 * self.diameter_main_top),
                   self.diameter_main_top,
                   self.diameter_main_top),
                  ((
                           start_point_x + self.width_support_left + self.beam_span + self.width_support_right - self.cover_view_right - 0.5 * self.diameter_main_top - bending),
                   (
                           start_point_y + self.beam_height - self.cover_top - self.diameter_stirrup - 0.5 * self.diameter_main_top),
                   self.diameter_main_top,
                   self.diameter_main_top, bugle),
                  ((
                           start_point_x + self.width_support_left + self.beam_span + self.width_support_right - self.cover_view_right - 0.5 * self.diameter_main_top),
                   (
                           start_point_y + self.beam_height - self.cover_top - self.diameter_stirrup - 0.5 * self.diameter_main_top - bending),
                   self.diameter_main_top, self.diameter_main_top),
                  ((
                           start_point_x + self.width_support_left + self.beam_span + self.width_support_right - self.cover_view_right - 0.5 * self.diameter_main_top),
                   start_point_y + self.cover_bottom)]
        self.msp.add_lwpolyline(points, dxfattribs={'closed': False, 'layer': self.bar})

        length_bar = self.length_bar(points=points, diameter=self.diameter_main_top)

        if dimension:
            self.list_bar(diameter=self.diameter_main_top, quantity_bar=quantity_bar, length=length_bar,
                          steel_grade=steel_grade,
                          points=(points[0][0] + (points[-1][0] - points[0][0]) / 2, points[3][1]))
            half = 0.5 * self.diameter_main_top
            self.dimension_generator(
                (points[0][0] - 25, points[0][1]), points[0][:2], (points[2][0], points[2][1] + half), angle=90,
                dimstyle=self.dim_name_bar
            )
            self.dimension_generator(
                (points[3][0], points[3][1] - 100), (points[1][0] - half, points[1][1]),
                (points[4][0] + half, points[4][1]), dimstyle=self.dim_name_bar
            )
            self.dimension_generator(
                (points[5][0] + 100, points[5][1]), (points[3][0], points[3][1] + half), points[5][:2], angle=90,
                dimstyle=self.dim_name_bar
            )

    def view_bottom_bar(self, quantity_bar: int, steel_grade: str, dimension: bool = False, start_point_x: float = None,
                        start_point_y: float = None):
        """generowanie pręta dolnego"""

        if start_point_x is None:
            start_point_x = self.position['main_bar_bottom'][0] if dimension else self.position['main_beam'][0]
        if start_point_y is None:
            start_point_y = self.position['main_bar_bottom'][1] if dimension else self.position['main_beam'][1]

        points = [((start_point_x + self.cover_view_left),
                   (start_point_y + self.cover_bottom + self.diameter_stirrup + 0.5 * self.diameter_main_bottom),
                   self.diameter_main_bottom, self.diameter_main_bottom),
                  (
                      start_point_x + self.width_support_left + self.beam_span + self.width_support_right - self.cover_view_right,
                      (start_point_y + self.cover_bottom + self.diameter_stirrup + 0.5 * self.diameter_main_bottom))]
        self.msp.add_lwpolyline(points, dxfattribs={'closed': False, 'layer': self.bar})

        length_bar = self.length_bar(points=points, diameter=self.diameter_main_bottom)

        if dimension:
            self.list_bar(diameter=self.diameter_main_bottom, quantity_bar=quantity_bar, length=length_bar,
                          steel_grade=steel_grade,
                          points=(points[0][0] + (points[-1][0] - points[0][0]) / 2, points[0][1]))
            self.dimension_generator(
                (points[0][0], points[0][1] - 100), points[0][:2], points[1][:2], dimstyle=self.dim_name_bar
            )

    def distance_from_supports(self, distance: float) -> float:
        value = 0

        if self.first_row_stirrup_range_left != 0 and self.first_row_stirrup_spacing_left != 0:
            value += math.ceil(
                self.first_row_stirrup_range_left / self.first_row_stirrup_spacing_left) * self.first_row_stirrup_spacing_left
        else:
            value += 0

        if self.first_row_stirrup_range_right != 0 and self.first_row_stirrup_spacing_right != 0:
            value += math.ceil(
                self.first_row_stirrup_range_right / self.first_row_stirrup_spacing_right) * self.first_row_stirrup_spacing_right
        else:
            value += 0

        return self.beam_span - (value + math.floor((self.beam_span - value) / distance) * distance)

    def stirrup_spacing(self):
        """rozstaw strzemion w belce"""
        last_stirrup_left: float = 0
        last_stirrup_right: float = self.beam_span
        localization_stirrups = []
        start_point_x, start_point_y = self.position['main_beam']
        range_first_row = self.distance_from_supports(self.secondary_stirrup_spacing)

        while range_first_row > 60:
            self.secondary_stirrup_spacing -= 5
            range_first_row = self.distance_from_supports(self.secondary_stirrup_spacing)

        if self.first_row_stirrup_range_left != 0 and self.first_row_stirrup_spacing_left != 0:
            for i in range(int(math.ceil(self.first_row_stirrup_range_left / self.first_row_stirrup_spacing_left) + 1)):
                localization_stirrups.append(range_first_row / 2 + i * self.first_row_stirrup_spacing_left)
            last_stirrup_left = localization_stirrups[-1]
            self.dimension_points.append(last_stirrup_left)

        if self.first_row_stirrup_range_right != 0 and self.first_row_stirrup_spacing_right != 0:
            for i in range(
                    int(math.ceil(self.first_row_stirrup_range_right / self.first_row_stirrup_spacing_right) + 1)):
                localization_stirrups.append(
                    self.beam_span - range_first_row / 2 - i * self.first_row_stirrup_spacing_right)
            last_stirrup_right = localization_stirrups[-1]
            self.dimension_points.append(last_stirrup_right)

        self.dimension_points.append(range_first_row / 2)
        self.dimension_points.append(self.beam_span - range_first_row / 2)

        self.dimension_points = list(dict.fromkeys(self.dimension_points))
        self.dimension_points.sort()

        for i in range(int((self.beam_span - last_stirrup_left - (
                (
                        self.beam_span - last_stirrup_right) if last_stirrup_right > 0 else 0)) / self.secondary_stirrup_spacing) + 1):
            localization_stirrups.append((
                                             last_stirrup_left if last_stirrup_left > 0 else range_first_row / 2) + i * self.secondary_stirrup_spacing)

        localization_stirrups = list(dict.fromkeys(localization_stirrups))
        localization_stirrups.sort()

        self.number_of_stirrups_of_the_second_row = math.ceil(
            (last_stirrup_right - last_stirrup_left) / self.secondary_stirrup_spacing)

        for i in localization_stirrups:
            points_stirrups = [
                (
                    (start_point_x + self.width_support_left + i), start_point_y + self.cover_bottom,
                    self.diameter_stirrup,
                    self.diameter_stirrup),
                ((start_point_x + self.width_support_left + i), start_point_y + (self.beam_height - self.cover_top))]
            self.msp.add_lwpolyline(points_stirrups, dxfattribs={'layer': self.stirrup})
        self.count_stirrups = len(localization_stirrups)

    def supports(self, value_left: float, value_right: float, height: int = 200, hatch_name: str = 'ANSI32'):
        start_point_x, start_point_y = self.position['main_beam']
        hatch = self.msp.add_hatch(dxfattribs={'layer': self.hatch})
        hatch.set_pattern_fill(hatch_name, scale=10, color=-1)
        hatch.paths.add_polyline_path(
            [(value_left, start_point_y), (value_left, start_point_y - height),
             (value_right, start_point_y - height), (value_right, start_point_y)]
        )

        line_point_left = [(value_left, start_point_y), (value_left, start_point_y - height)]
        line_point_right = [(value_right, start_point_y), (value_right, start_point_y - height)]

        self.msp.add_lwpolyline(line_point_left, dxfattribs={'layer': self.counter})
        self.msp.add_lwpolyline(line_point_right, dxfattribs={'layer': self.counter})

        line_hidden = [(value_left - 200, start_point_y - height),
                       (value_right + 200, start_point_y - height)]

        self.msp.add_lwpolyline(line_hidden, dxfattribs={'layer': self.hidden})

    def dimension_generator(self, base: tuple, p1: tuple, p2: tuple, angle: float = 0, text: str = "<>",
                            dimstyle=None) -> object:
        if dimstyle is None:
            dimstyle = self.dim_name
        return self.msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle, dimstyle=dimstyle,
                                       dxfattribs={'layer': self.dimension},
                                       text=text)

    def dimension_main(self, height: int = 400):
        start_point_x, start_point_y = self.position['main_beam']
        self.dimension_generator(
            (start_point_x, start_point_y - height),
            (start_point_x, start_point_y - height),
            (start_point_x + self.width_support_left, start_point_y - height)
        )

        self.dimension_generator(
            (start_point_x, start_point_y - height),
            (start_point_x + self.width_support_left, start_point_y - height),
            (start_point_x + self.width_support_left + self.beam_span, start_point_y - height)
        )

        self.dimension_generator(
            (start_point_x, start_point_y - height),
            (start_point_x + self.width_support_left + self.beam_span, start_point_y - height),
            (start_point_x + self.width_support_left + self.beam_span + self.width_support_right,
             start_point_y - height)
        )

        self.dimension_generator(
            (start_point_x - 200, start_point_y),
            (start_point_x, start_point_y),
            (start_point_x, start_point_y + self.beam_height),
            90
        )

    def dimension_stirrup(self, height: float = 300):
        value1, value2, value3, value4, value5, value6 = 0, 0, 0, 0, 0, self.beam_span
        start_end_dimension: bool = False
        start_point_x, start_point_y = self.position['main_beam']
        if len(self.dimension_points) == 2:
            value3 = 0
            value4 = self.beam_span
            self.number_of_stirrups_of_the_second_row += 1
        elif len(
                self.dimension_points) == 3 and self.first_row_stirrup_range_left != 0 and self.first_row_stirrup_spacing_left != 0:
            value3 = 0
            value4 = self.dimension_points[1]
            value5 = self.beam_span
        elif len(
                self.dimension_points) == 3 and self.first_row_stirrup_range_right != 0 and self.first_row_stirrup_spacing_right != 0:
            value2 = 0
            value3 = self.dimension_points[1]
            value4 = self.beam_span
        elif len(self.dimension_points) == 4 and (self.dimension_points[1] - self.dimension_points[0]) > 30:
            value2 = self.dimension_points[0]
            value3 = self.dimension_points[1]
            value4 = self.dimension_points[2]
            value5 = self.dimension_points[3]
        elif len(self.dimension_points) == 4:
            value2 = self.dimension_points[1]
            value3 = self.dimension_points[1]
            value4 = self.dimension_points[2]
            value5 = self.dimension_points[2]
            start_end_dimension = True
            self.number_of_stirrups_of_the_second_row -= 1
        elif len(
                self.dimension_points) == 5 and self.first_row_stirrup_range_left != 0 and self.first_row_stirrup_spacing_left != 0:
            value2 = self.dimension_points[1]
            value3 = self.dimension_points[2]
            value4 = self.dimension_points[3]
            value5 = self.dimension_points[3]
            start_end_dimension = True
            self.number_of_stirrups_of_the_second_row -= 1
        elif len(
                self.dimension_points) == 5 and self.first_row_stirrup_range_right != 0 and self.first_row_stirrup_spacing_right != 0:
            value2 = self.dimension_points[1]
            value3 = self.dimension_points[1]
            value4 = self.dimension_points[2]
            value5 = self.dimension_points[3]
            start_end_dimension = True
            self.number_of_stirrups_of_the_second_row -= 1
        elif len(self.dimension_points) == 6:
            value2 = self.dimension_points[1]
            value3 = self.dimension_points[2]
            value4 = self.dimension_points[3]
            value5 = self.dimension_points[4]
            start_end_dimension = True
        else:
            print('error 1. Błąd generatora wymiarowania', self.dimension_points)

        if start_end_dimension:
            self.dimension_generator(
                (start_point_x, start_point_y - height),
                (start_point_x + self.width_support_left + value1, start_point_y - height),
                (start_point_x + self.width_support_left + value2, start_point_y - height)
            )

            self.dimension_generator(
                (start_point_x, start_point_y - height),
                (start_point_x + self.width_support_left + value5, start_point_y - height),
                (start_point_x + self.width_support_left + value6, start_point_y - height)
            )

        if self.first_row_stirrup_range_left != 0 and self.first_row_stirrup_spacing_left != 0:
            self.dimension_generator(
                (start_point_x, start_point_y - height),
                (start_point_x + self.width_support_left + value2,
                 start_point_y - height),
                (start_point_x + self.width_support_left + value3,
                 start_point_y - height),
                text=f'{math.ceil((value3 - value2) / self.first_row_stirrup_spacing_left)} x {self.first_row_stirrup_spacing_left} = <>'
            )

        if self.first_row_stirrup_range_right != 0 and self.first_row_stirrup_spacing_right != 0:
            self.dimension_generator(
                (start_point_x, start_point_y - height),
                (start_point_x + self.width_support_left + value5,
                 start_point_y - height),
                (start_point_x + self.width_support_left + value4,
                 start_point_y - height),
                text=f'{math.ceil((value5 - value4) / self.first_row_stirrup_spacing_right)} x {self.first_row_stirrup_spacing_right} = <>'
            )

        if self.number_of_stirrups_of_the_second_row != 0:
            self.dimension_generator(
                (start_point_x, start_point_y - height),
                (start_point_x + self.width_support_left + value3,
                 start_point_y - height),
                (start_point_x + self.width_support_left + value4,
                 start_point_y - height),
                text=f'{math.ceil((value4 - value3) / self.number_of_stirrups_of_the_second_row)} x {self.number_of_stirrups_of_the_second_row} = <>'
            )

    def bar_section(self, diameter: float, point: list[tuple[float, float]]):
        for i in point:
            self.msp.add_circle(i, diameter / 2, dxfattribs={"layer": self.bar})
            self.msp.add_hatch(color=-1, dxfattribs={"layer": self.hatch}).paths.add_edge_path().add_arc(i,
                                                                                                         diameter / 2)

    def localization_bar_section(self, localization: Literal['top', 'bottom']) -> list[tuple[float, float]]:
        start_point_x, start_point_y = self.position['section']
        bar = {}
        turn = 1
        list_points = []
        center = 0
        if localization == 'top':
            bar = self.steel_bill[0]
            start_point_y += self.beam_height
            turn = -1
            center = self.cover_top + self.diameter_stirrup + bar['diameter'] / 2
        elif localization == 'bottom':
            bar = self.steel_bill[1]
            center = self.cover_bottom + self.diameter_stirrup + bar['diameter'] / 2

        bending = self.bar_bending(self.diameter_stirrup)
        first_bar_horizontal = (
            self.cover_left + self.diameter_stirrup / 2 + bending,
            self.beam_width - self.cover_right - self.diameter_stirrup / 2 - bending) \
            if bending - self.diameter_stirrup / 2 >= bar['diameter'] / 2 \
            else (
            self.cover_left + self.diameter_stirrup + bar['diameter'] / 2,
            self.beam_width - self.cover_right - self.diameter_stirrup - bar['diameter'] / 2)

        value = spacing_between_bars(bar['diameter'])

        count_bar_next_line = 0
        while (first_bar_horizontal[1] - first_bar_horizontal[0]) / (
                bar['quantity_bar'] - count_bar_next_line - 1) < value:
            count_bar_next_line += 1

        spacing_first_line = first_bar_horizontal[1] - first_bar_horizontal[0]
        first_line = bar['quantity_bar'] - count_bar_next_line

        for i in range(first_line):
            list_points.append(
                (start_point_x + first_bar_horizontal[0] + spacing_first_line / (first_line - 1) * i,
                 start_point_y + turn * center))

        if count_bar_next_line > 0:
            if count_bar_next_line == 1:
                list_points.append(
                    (start_point_x + self.cover_left + self.diameter_stirrup + bar['diameter'] / 2,
                     start_point_y + turn * (center + value)))
            else:
                second_bar_horizontal = (
                    self.cover_left + self.diameter_stirrup + bar['diameter'] / 2,
                    self.beam_width - self.cover_left - self.diameter_stirrup - bar['diameter'] / 2
                )
                spacing_second_line = second_bar_horizontal[1] - second_bar_horizontal[0]
                if (second_bar_horizontal[1] - second_bar_horizontal[0]) / (count_bar_next_line if count_bar_next_line == 1 else count_bar_next_line - 1) >= value:
                    for i in range(count_bar_next_line):
                        list_points.append((start_point_x + second_bar_horizontal[0] + spacing_second_line / (count_bar_next_line - 1) * i, start_point_y + turn * (center + value)))
                else:
                    self.msp.add_text("Nie poprawny rozstaw prętów, zmień przekrój belki lub prętów!!", dxfattribs={'height': 500, 'style': self.text})\
                        .set_placement((start_point_x + self.beam_span, start_point_y + 2 * self.beam_height), align=TextEntityAlignment.MIDDLE_CENTER)

        return list_points

    def beam_section_rectangular(self):
        start_point_x, start_point_y = self.position['section']

        self.msp.add_text('A-A', dxfattribs={"height": 5 * 20, 'style': self.text, "layer": self.counter}) \
            .set_placement((start_point_x + self.beam_height / 2, start_point_y + self.beam_height + 200),
                           align=TextEntityAlignment.BOTTOM_CENTER)

        points_beam_section = [(start_point_x, start_point_y),
                               (start_point_x + self.beam_width, start_point_y),
                               (start_point_x + self.beam_width, start_point_y + self.beam_height),
                               (start_point_x, start_point_y + self.beam_height)]

        self.msp.add_lwpolyline(points_beam_section, dxfattribs={'closed': True, 'layer': self.counter})
        self.view_stirrups_type_1(start_point_x, start_point_y)

        self.bar_section(self.diameter_main_bottom, self.localization_bar_section('bottom'))
        self.bar_section(self.diameter_main_top, self.localization_bar_section('top'))
        start_for_line = []
        for value, (x0, y0) in enumerate(self.localization_bar_section('top')):
            x1 = (x0 + (start_point_y + self.beam_height + 100 - y0) * math.tan(math.pi / 2 - math.radians(60)))
            if value == 0:
                start_for_line.append(x1)
            self.msp.add_lwpolyline(
                [(x0, y0),
                 (x1,
                  (start_point_y + self.beam_height + 100))],
                dxfattribs={'layer': self.counter})
        for value, (x0, y0) in enumerate(self.localization_bar_section('bottom')):
            x1 = (x0 + (y0 - start_point_y + 100) * math.tan(2 * math.pi + math.radians(30)))
            if value == 0:
                start_for_line.append(x1)
            self.msp.add_lwpolyline(
                [(x0, y0),
                 (x1,
                  (start_point_y - 100))
                 ],
                dxfattribs={'layer': self.counter})
        self.msp.add_lwpolyline([(start_for_line[0], start_point_y + self.beam_height + 100),
                                 ((start_point_x + self.beam_width + 100), (start_point_y + self.beam_height + 100))],
                                dxfattribs={'layer': self.counter})
        self.msp.add_lwpolyline([(start_for_line[1], start_point_y - 100),
                                 ((start_point_x + self.beam_width + 100), (start_point_y - 100))],
                                dxfattribs={'layer': self.counter})
        self.msp.add_lwpolyline(
            [(start_point_x + self.beam_width - self.cover_right, start_point_y + self.beam_height / 2),
             (start_point_x + self.beam_width + 100, start_point_y + self.beam_height / 2)],
            dxfattribs={'layer': self.counter})
        # todo: Poprawić ponieważ powinno samo nadawać nr pręta
        self.generate_marker_left(((start_point_x + self.beam_width + 100), (start_point_y + self.beam_height + 100)),
                                  1)
        self.generate_marker_left(((start_point_x + self.beam_width + 100), (start_point_y - 100)), 2)
        self.generate_marker_left((start_point_x + self.beam_width + 100, start_point_y + self.beam_height / 2), 3)

        self.dimension_section()

    def dimension_section(self, height: int = 200):
        start_point_x, start_point_y = self.position['section']
        self.dimension_generator(
            (start_point_x, start_point_y - height),
            (start_point_x, start_point_y - height),
            (start_point_x + self.beam_width, start_point_y - height)
        )

        self.dimension_generator(
            (start_point_x - height / 4, start_point_y),
            (start_point_x, start_point_y),
            (start_point_x, start_point_y + self.beam_height),
            angle=90
        )

    def view_stirrups_type_1(self, start_point_x: float, start_point_y: float, anchoring_stirrup: float = 80):

        bending_stirrup = self.bar_bending(self.diameter_stirrup)
        bending_arrow = self.bar_bulge(bending_stirrup)

        points = [
            (start_point_x + self.cover_left + 0.5 * self.diameter_stirrup,
             start_point_y + self.beam_height - self.cover_top - 0.5 * self.diameter_stirrup - bending_stirrup - anchoring_stirrup,
             self.diameter_stirrup, self.diameter_stirrup),
            (start_point_x + self.cover_left + 0.5 * self.diameter_stirrup,
             start_point_y + self.beam_height - self.cover_top - 0.5 * self.diameter_stirrup - bending_stirrup,
             self.diameter_stirrup, self.diameter_stirrup, bending_arrow),
            (start_point_x + self.cover_left + 0.5 * self.diameter_stirrup + bending_stirrup,
             start_point_y + self.beam_height - self.cover_top - 0.5 * self.diameter_stirrup, self.diameter_stirrup,
             self.diameter_stirrup),
            (start_point_x + self.beam_width - self.cover_right - 0.5 * self.diameter_stirrup - bending_stirrup,
             start_point_y + self.beam_height - self.cover_top - 0.5 * self.diameter_stirrup, self.diameter_stirrup,
             self.diameter_stirrup, bending_arrow),
            (start_point_x + self.beam_width - self.cover_right - 0.5 * self.diameter_stirrup,
             start_point_y + self.beam_height - self.cover_top - 0.5 * self.diameter_stirrup - bending_stirrup,
             self.diameter_stirrup, self.diameter_stirrup),
            (start_point_x + self.beam_width - self.cover_right - 0.5 * self.diameter_stirrup,
             start_point_y + self.cover_bottom + 0.5 * self.diameter_stirrup + bending_stirrup, self.diameter_stirrup,
             self.diameter_stirrup, bending_arrow),
            (start_point_x + self.beam_width - self.cover_right - 0.5 * self.diameter_stirrup - bending_stirrup,
             start_point_y + self.cover_bottom + 0.5 * self.diameter_stirrup, self.diameter_stirrup,
             self.diameter_stirrup),
            (start_point_x + self.cover_left + 0.5 * self.diameter_stirrup + bending_stirrup,
             start_point_y + self.cover_bottom + 0.5 * self.diameter_stirrup, self.diameter_stirrup,
             self.diameter_stirrup, bending_arrow),
            (start_point_x + self.cover_left + 0.5 * self.diameter_stirrup,
             start_point_y + self.cover_bottom + 0.5 * self.diameter_stirrup + bending_stirrup, self.diameter_stirrup,
             self.diameter_stirrup),
            (start_point_x + self.cover_left + 0.5 * self.diameter_stirrup,
             start_point_y + self.beam_height - self.cover_top - 0.5 * self.diameter_stirrup - bending_stirrup,
             self.diameter_stirrup, self.diameter_stirrup, bending_arrow),
            (start_point_x + self.cover_left + 0.5 * self.diameter_stirrup + bending_stirrup,
             start_point_y + self.beam_height - self.cover_top - 0.5 * self.diameter_stirrup, self.diameter_stirrup,
             self.diameter_stirrup),
            (start_point_x + self.cover_left + 0.5 * self.diameter_stirrup + bending_stirrup + anchoring_stirrup,
             start_point_y + self.beam_height - self.cover_top - 0.5 * self.diameter_stirrup, self.diameter_stirrup,
             self.diameter_stirrup)
        ]
        length_bar = self.length_bar(points=points, diameter=self.diameter_stirrup)

        self.list_bar(diameter=self.diameter_stirrup, quantity_bar=self.count_stirrups, length=length_bar,
                      steel_grade=self.steel_grade_stirrup, points=(0, 0))

        self.msp.add_lwpolyline(points, dxfattribs={'layer': self.bar})

    def view_stirrups_type_2(self, anchoring_stirrup: float = (10 * 8)):
        bending_stirrup = self.bar_bending(self.diameter_stirrup)
        start_point_x, start_point_y = self.position['stirrup']

        theta = 60

        point_1 = point_position(start_point_x + self.cover_left + 0.5 * self.diameter_stirrup,
                                 start_point_y + self.beam_height - self.cover_top - 0.5 * self.diameter_stirrup,
                                 self.beam_width - self.diameter_stirrup - self.cover_left - self.cover_right, theta)

        point_2 = point_position(point_1[0], point_1[1], bending_stirrup + anchoring_stirrup, 90 + theta)

        points = [(
            start_point_x + self.beam_width - self.cover_left - 0.5 * self.diameter_stirrup - bending_stirrup - anchoring_stirrup,
            start_point_y + self.beam_height - self.cover_top - 0.5 * self.diameter_stirrup,
            self.diameter_stirrup,
            self.diameter_stirrup),
            (start_point_x + self.beam_width - self.cover_left - 0.5 * self.diameter_stirrup,
             start_point_y + self.beam_height - self.cover_top - 0.5 * self.diameter_stirrup,
             self.diameter_stirrup,
             self.diameter_stirrup),
            (start_point_x + self.beam_width - self.cover_left - 0.5 * self.diameter_stirrup,
             start_point_y + self.cover_bottom + 0.5 * self.diameter_stirrup,
             self.diameter_stirrup,
             self.diameter_stirrup
             ),
            (start_point_x + self.cover_left + 0.5 * self.diameter_stirrup,
             start_point_y + self.cover_bottom + 0.5 * self.diameter_stirrup,
             self.diameter_stirrup,
             self.diameter_stirrup
             ),
            (start_point_x + self.cover_left + 0.5 * self.diameter_stirrup,
             start_point_y + self.beam_height - self.cover_top - 0.5 * self.diameter_stirrup,
             self.diameter_stirrup,
             self.diameter_stirrup
             ),
            (start_point_x + self.cover_left + 0.5 * self.diameter_stirrup,
             start_point_y + self.beam_height - self.cover_top - 0.5 * self.diameter_stirrup,
             self.diameter_stirrup,
             self.diameter_stirrup
             ),
            (
                point_1[0],
                point_1[1],
                self.diameter_stirrup,
                self.diameter_stirrup
            ),
            (
                point_2[0],
                point_2[1],
                self.diameter_stirrup,
                self.diameter_stirrup
            )

        ]

        self.msp.add_lwpolyline(points, dxfattribs={'layer': self.bar})

        self.msp.add_linear_dim((start_point_x, start_point_y - 50),
                                (start_point_x + self.cover_left, start_point_y + self.cover_bottom), (
                                    start_point_x + self.beam_width - self.cover_right,
                                    start_point_y + self.cover_bottom), dimstyle=self.dim_name_bar,
                                dxfattribs={'layer': self.dimension}, angle=0, text='<>')
        # dimension left
        self.msp.add_linear_dim(
            (start_point_x + self.cover_left - 25, start_point_y),
            (start_point_x + self.cover_left, start_point_y + self.cover_bottom),
            (start_point_x + self.cover_left, start_point_y + self.beam_height - self.cover_top),
            dimstyle=self.dim_name_bar,
            dxfattribs={'layer': self.dimension}, angle=90, text='<>')
        self.steel_bill[-1]['points_generate'] = (
            start_point_x + self.beam_width - self.cover_right + 400, start_point_y + self.beam_height / 2 - 100)

    # def generate_cell(self, points: list[tuple[float, float]], scale: int = 20, text: str = "__"):

    def generate_cell(self, point_top_left: tuple[float, float], width: float, height: float, scale: int = 20,
                      text: str = "__", height_text: float = 2.5, attachment_point: int = 5):

        """ MTEXT_TOP_LEFT          1
            MTEXT_TOP_CENTER        2
            MTEXT_TOP_RIGHT         3
            MTEXT_MIDDLE_LEFT       4
            MTEXT_MIDDLE_CENTER     5
            MTEXT_MIDDLE_RIGHT      6
            MTEXT_BOTTOM_LEFT       7
            MTEXT_BOTTOM_CENTER     8
            MTEXT_BOTTOM_RIGHT      9
        """

        points = [point_top_left,
                  (point_top_left[0] + width * scale, point_top_left[1]),
                  (point_top_left[0] + width * scale, point_top_left[1] - height * scale),
                  (point_top_left[0], point_top_left[1] - height * scale)]

        self.msp.add_lwpolyline(points, dxfattribs={'closed': True, 'layer': self.counter})

        if attachment_point == 5:
            location = (tuple(map(lambda x: sum(x) / float(len(x)), zip(*points[:3:2]))))
        elif attachment_point == 4:
            location = (point_top_left[0] + 1 * scale, point_top_left[1] - height / 2 * scale)
        elif attachment_point == 6:
            location = (point_top_left[0] + (width - 1) * scale, point_top_left[1] - height / 2 * scale)
        else:
            location = (tuple(map(lambda x: sum(x) / float(len(x)), zip(*points[:3:2]))))

        self.msp.add_mtext(text,
                           dxfattribs={'style': self.text,
                                       'char_height': scale * height_text,
                                       'attachment_point': attachment_point,
                                       'layer': self.counter}) \
            .set_location(location)

    def create_table(self, steel_bill: list, scale: int = 20):
        start_point_x, start_point_y = self.position['bending_schedule']

        steel_grade = {}
        for i in steel_bill:
            value_grade = i['steel_grade']
            if value_grade not in steel_grade:
                steel_grade[value_grade] = []

        for i in steel_bill:
            value_diameter = i['diameter']
            value_grade = i['steel_grade']
            for j in steel_grade:
                if value_grade == j:
                    if value_diameter not in steel_grade[value_grade]:
                        steel_grade[value_grade].append(value_diameter)

        count_column = sum(len(value) for value in steel_grade.values())
        count_row = len(steel_bill)

        column_width = [10, 15, 15, 15, 15, 15 * count_column, 20]
        row_height = [10, 5, 5, 5, 5, 5 * count_row, 5]

        start_point = (start_point_x, start_point_y)

        # title
        self.generate_cell(point_top_left=start_point, width=sum(column_width), height=row_height[0],
                           text=LANG['bending_schedule'], height_text=5)
        # header
        self.generate_cell(point_top_left=tuple_dest(start_point,
                                                     height=-sum(row_height[:1]) * scale),
                           width=column_width[0],
                           height=sum(row_height[1:4]),
                           text=LANG['mark'])

        self.generate_cell(point_top_left=tuple_dest(start_point,
                                                     height=-sum(row_height[:1]) * scale,
                                                     width=sum(column_width[:1]) * scale),
                           width=column_width[1],
                           height=sum(row_height[1:3]),
                           text=LANG['dia'])

        self.generate_cell(point_top_left=tuple_dest(start_point,
                                                     height=-sum(row_height[:3]) * scale,
                                                     width=sum(column_width[:1]) * scale),
                           width=column_width[1],
                           height=sum(row_height[3:4]),
                           text=LANG['length_mm'])

        self.generate_cell(point_top_left=tuple_dest(start_point,
                                                     height=-sum(row_height[:1]) * scale,
                                                     width=sum(column_width[:2]) * scale),
                           width=column_width[2],
                           height=sum(row_height[1:3]),
                           text=LANG['length_bar'])

        self.generate_cell(point_top_left=tuple_dest(start_point,
                                                     height=-sum(row_height[:3]) * scale,
                                                     width=sum(column_width[:2]) * scale),
                           width=column_width[2],
                           height=sum(row_height[3:4]),
                           text=LANG['length_mm'])

        self.generate_cell(point_top_left=tuple_dest(start_point,
                                                     height=-sum(row_height[:1]) * scale,
                                                     width=sum(column_width[:3]) * scale),
                           width=column_width[3],
                           height=sum(row_height[1:3]),
                           text=LANG['number_in_element'])

        self.generate_cell(point_top_left=tuple_dest(start_point,
                                                     height=-sum(row_height[:3]) * scale,
                                                     width=sum(column_width[:3]) * scale),
                           width=column_width[3],
                           height=sum(row_height[3:4]),
                           text=LANG['pcs'])

        self.generate_cell(point_top_left=tuple_dest(start_point,
                                                     height=-sum(row_height[:1]) * scale,
                                                     width=sum(column_width[:4]) * scale),
                           width=column_width[4],
                           height=sum(row_height[1:3]),
                           text=LANG['total_number'])

        self.generate_cell(point_top_left=tuple_dest(start_point,
                                                     height=-sum(row_height[:3]) * scale,
                                                     width=sum(column_width[:4]) * scale),
                           width=column_width[4],
                           height=sum(row_height[3:4]),
                           text=LANG['pcs'])

        self.generate_cell(point_top_left=tuple_dest(start_point,
                                                     height=-sum(row_height[:1]) * scale,
                                                     width=sum(column_width[:5]) * scale),
                           width=column_width[5],
                           height=sum(row_height[3:4]),
                           text=LANG['total_length'])

        # nie należy tak tworzyć tablic, listy należy tworzyć przez list comprechention
        # array_bending_schedule = count_column * [count_row * [0]]

        array_bending_schedule = [['-' for i in range(count_column)] for j in range(count_row)]
        count_count_grade_value = 0

        for i in steel_grade:
            count_column_grade = column_width[5] * count_count_grade_value / count_column

            self.generate_cell(point_top_left=tuple_dest(start_point,
                                                         height=-sum(row_height[:2]) * scale,
                                                         width=(sum(column_width[:5]) + count_column_grade) * scale),
                               width=column_width[5] / count_column * len(steel_grade[i]),
                               height=sum(row_height[3:4]),
                               text=i)

            for j in range(len(steel_grade[i])):
                self.generate_cell(point_top_left=tuple_dest(start_point,
                                                             height=-sum(row_height[:3]) * scale,
                                                             width=(sum(column_width[
                                                                        :5]) + column_width[
                                                                        5] * count_count_grade_value / count_column) * scale),
                                   width=column_width[5] / count_column,
                                   height=sum(row_height[4:5]),
                                   text=f'%%c{steel_grade[i][j]}')

                for k in range(len(steel_bill)):
                    if steel_bill[k]['steel_grade'] == i and steel_bill[k]['diameter'] == steel_grade[i][j]:
                        array_bending_schedule[k][count_count_grade_value] = round(
                            steel_bill[k]['length'] / 1000 * steel_bill[k]['quantity_bar'] * self.number_of_elements, 2)

                count_count_grade_value += 1

        if column_width[6] > 0:
            self.generate_cell(point_top_left=tuple_dest(start_point,
                                                         height=-sum(row_height[:1]) * scale,
                                                         width=sum(column_width[:6]) * scale),
                               width=column_width[6],
                               height=sum(row_height[1:4]),
                               text=LANG['comments'])

        elements = []
        for i in steel_bill:
            value_element = i['name_element']
            if value_element not in elements:
                elements.append(value_element)
        elements.sort()

        for i in range(len(elements)):
            self.generate_cell(point_top_left=tuple_dest(start_point,
                                                         height=-sum(row_height[:4]) * scale),
                               width=sum(column_width[:]),
                               height=sum(row_height[4:5]),
                               attachment_point=4,
                               text=f"{LANG['element:']} {self.name}")
            self.generate_cell(point_top_left=tuple_dest(start_point,
                                                         height=-sum(row_height[:4]) * scale),
                               width=sum(column_width[:]),
                               height=sum(row_height[4:5]),
                               attachment_point=6,
                               text=f"{LANG['make']} {self.number_of_elements} {LANG['pcs']}")
            for j in range(count_row):
                self.generate_cell(point_top_left=tuple_dest(start_point,
                                                             height=-(sum(row_height[:5]) + row_height[
                                                                 5] * j / count_row) * scale),
                                   width=column_width[0],
                                   height=row_height[5] / count_row,
                                   text=steel_bill[j]['number'])

                self.generate_cell(point_top_left=tuple_dest(start_point,
                                                             height=-(sum(row_height[:5]) + row_height[
                                                                 5] * j / count_row) * scale,
                                                             width=sum(column_width[:1]) * scale),

                                   width=column_width[1],
                                   height=row_height[5] / count_row,
                                   text=f"%%c {steel_bill[j]['diameter']}")

                self.generate_cell(point_top_left=tuple_dest(start_point,
                                                             height=-(sum(row_height[:5]) + row_height[
                                                                 5] * j / count_row) * scale,
                                                             width=sum(column_width[:2]) * scale),

                                   width=column_width[2],
                                   height=row_height[5] / count_row,
                                   text=steel_bill[j]['length'])

                self.generate_cell(point_top_left=tuple_dest(start_point,
                                                             height=-(sum(row_height[:5]) + row_height[
                                                                 5] * j / count_row) * scale,
                                                             width=sum(column_width[:3]) * scale),

                                   width=column_width[3],
                                   height=row_height[5] / count_row,
                                   text=steel_bill[j]['quantity_bar'])

                self.generate_cell(point_top_left=tuple_dest(start_point,
                                                             height=-(sum(row_height[:5]) + row_height[
                                                                 5] * j / count_row) * scale,
                                                             width=sum(column_width[:4]) * scale),

                                   width=column_width[4],
                                   height=row_height[5] / count_row,
                                   text=f"{steel_bill[j]['quantity_bar'] * self.number_of_elements}")

                for k in range(count_column):
                    self.generate_cell(point_top_left=tuple_dest(start_point,
                                                                 height=-(sum(row_height[:5]) + row_height[
                                                                     5] * j / count_row) * scale,
                                                                 width=(sum(column_width[:5]) + column_width[
                                                                     5] * k / count_column) * scale),

                                       width=column_width[5] / count_column,
                                       height=row_height[5] / count_row,
                                       text=f"{array_bending_schedule[j][k]}")

                if column_width[6] > 0:
                    self.generate_cell(point_top_left=tuple_dest(start_point,
                                                                 height=-(sum(row_height[:5]) + row_height[
                                                                     5] * j / count_row) * scale,
                                                                 width=sum(column_width[:6]) * scale),
                                       width=column_width[6],
                                       height=row_height[5] / count_row,
                                       text='')
        # footer
        array_total_mass = [[0 for i in range(count_column)] if j < 3 else [0] for j in range(4)]

        for i in range(len(array_bending_schedule[0])):
            for j in array_bending_schedule:
                if type(j[i]) is float:
                    array_total_mass[0][i] += j[i]

        count_count_grade_value = 0
        for i in steel_grade:
            for j in range(len(steel_grade[i])):
                for k in range(len(steel_bill)):
                    if steel_bill[k]['steel_grade'] == i and steel_bill[k]['diameter'] == steel_grade[i][j]:
                        array_total_mass[1][count_count_grade_value] = self.mass_1m_bar(steel_bill[k]['diameter'])
                count_count_grade_value += 1

        for i in range(len(array_total_mass[2])):
            value = array_total_mass[0][i] * array_total_mass[1][i]
            array_total_mass[2][i] = round(value, 1)
            array_total_mass[3][0] += round(value, 1)

        array_footer = [
            [(LANG['total_length_dia'], 4), (LANG['length_m'], 6)],
            [(LANG['mass_1m'], 4), (LANG['mass_length'], 6)],
            [(LANG['mass_according_dia'], 4), (LANG['mass'], 6)],
            [[LANG['mass_total'], 4], (LANG['mass'], 6)]
        ]

        for i in range(len(array_footer)):
            for j in range(len(array_footer[i])):
                self.generate_cell(point_top_left=tuple_dest(start_point,
                                                             height=-(sum(row_height[:6]) + row_height[6] * i) * scale),
                                   height=row_height[6],
                                   width=sum(column_width[:5]),
                                   attachment_point=array_footer[i][j][1],
                                   text=f"{array_footer[i][j][0]}")
            for j in range(len(array_total_mass[i])):
                self.generate_cell(point_top_left=tuple_dest(start_point,
                                                             height=-(sum(row_height[:6]) + row_height[6] * i) * scale,
                                                             width=(sum(column_width[:5]) + column_width[
                                                                 5] * j / count_column) * scale),
                                   height=row_height[6],
                                   width=column_width[5] / (count_column if len(array_total_mass[i]) > 1 else 1),
                                   attachment_point=6 if len(array_total_mass[i]) > 1 else 5,
                                   text=f"{round(array_total_mass[i][j], 3)}")
            if column_width[6] > 0:
                self.generate_cell(point_top_left=tuple_dest(start_point,
                                                             height=-(sum(row_height[:6]) + row_height[6] * i) * scale,
                                                             width=sum(column_width[:6]) * scale),
                                   height=row_height[6],
                                   width=column_width[6],
                                   text='')
        # todo: dodać pod tabelą uwagi

    def _create_block_marker_section(self):
        name = 'marker_section'
        if name in self.drawing.blocks:
            block = self.drawing.blocks.get(name)
        else:
            block = self.drawing.blocks.new(name)

        block.add_lwpolyline([(0, -4), (0, 4)])
        block.add_attdef('SECTION', dxfattribs={"height": 5, 'style': self.text, "layer": self.counter}).set_placement(
            (1, 0), align=TextEntityAlignment.MIDDLE_LEFT)

    def _create_block_marker_left(self):
        name = 'marker'
        if name in self.drawing.blocks:
            block = self.drawing.blocks.get(name)
        else:
            block = self.drawing.blocks.new(name)

        block.add_circle((4, 0), 4, dxfattribs={"layer": self.counter})
        block.add_attdef('NUMBER', dxfattribs={"height": 2.5, 'style': self.text, "layer": self.counter}).set_placement(
            (4, 0), align=TextEntityAlignment.MIDDLE_CENTER)

    def _create_block_reinforcement_description(self):
        name = "reinforcement_description"
        if name in self.drawing.blocks:
            block = self.drawing.blocks.get(name)
        else:
            block = self.drawing.blocks.new(name)

        block.add_circle((-14, 5), 4, dxfattribs={"layer": self.counter})
        block.add_attdef('NUMBER', dxfattribs={"height": 2.5, 'style': self.text, "layer": self.counter}).set_placement(
            (-14, 5), align=TextEntityAlignment.MIDDLE_CENTER)
        block.add_attdef('QUANTITY',
                         dxfattribs={"height": 2.5, 'style': self.text, "layer": self.counter}).set_placement((-4, 5),
                                                                                                              align=TextEntityAlignment.MIDDLE_RIGHT)
        block.add_text('%%c', dxfattribs={"height": 2.5, 'style': self.text, "layer": self.counter}).set_placement(
            (-2.5, 5), align=TextEntityAlignment.MIDDLE_CENTER)
        block.add_attdef('DIAMETER',
                         dxfattribs={"height": 2.5, 'style': self.text, "layer": self.counter}).set_placement((0, 5),
                                                                                                              align=TextEntityAlignment.MIDDLE_LEFT)
        block.add_text('L=', dxfattribs={"height": 2.5, 'style': self.text, "layer": self.counter}).set_placement(
            (5, 5), align=TextEntityAlignment.MIDDLE_LEFT)
        block.add_attdef('LENGTH', dxfattribs={"height": 2.5, 'style': self.text, "layer": self.counter}).set_placement(
            (9, 5), align=TextEntityAlignment.MIDDLE_LEFT)

    def generate_reinforcement_description(self, position: tuple, number: float or str, quantity: float or str,
                                           diameter: float or str,
                                           length: float or str, scale: int = 20):
        self.msp.add_auto_blockref("reinforcement_description", position,
                                   {"NUMBER": str(number), "QUANTITY": str(quantity), "DIAMETER": str(diameter),
                                    "LENGTH": str(length)}).set_scale(scale).explode()

    def generate_marker_left(self, position: tuple, number: float or str, scale: int = 20):
        self.msp.add_auto_blockref("marker", position, {"NUMBER": str(number)}).set_scale(scale).explode()

    def generate_marker_section(self, position: tuple, section: float or str, scale: int = 20):
        self.msp.add_auto_blockref("marker_section", position, {"SECTION": str(section).upper()}).set_scale(
            scale).explode()

    def generate_block(self):
        for i in self.steel_bill:
            self.generate_reinforcement_description(
                position=i['points_generate'],
                number=i['number'],
                quantity=i['quantity_bar'],
                diameter=i['diameter'],
                length=i['length']
            )

    def layout_new(self):
        """layauty, początki"""
        name = f"{self.name}"
        if name in self.drawing.layouts:
            layout = self.drawing.layouts.get(name)
        else:
            layout = self.drawing.layouts.new(name)

        layout.page_setup(
            size=(420, 297), margins=(0.5, 0.5, 0.5, 0.5), units="mm", scale=(1, 20)
        )
        # layout.add_viewport((420 / 2, 297 / 2), (419 * 20, 296 * 20), (420, 297), 296 * 20)
