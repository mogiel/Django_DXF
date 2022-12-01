import os
from django.http import HttpResponse
from django.shortcuts import render
from uuid import uuid4 as uuid
from calc.app.mainclass import DxfElement


# Create your views here.

def home(request):
    return render(request, 'home.html')


def beam(request):
    return render(request, 'beam.html')


def author(request):
    return render(request, 'author.html')


def download_dxf_beam(request):
    name = str(request.POST['name'])
    beam_span = float(request.POST['beam_span'])
    beam_height = float(request.POST['beam_height'])
    beam_width = float(request.POST['beam_width'])
    width_support_left = int(request.POST['width_support_left'])
    width_support_right = int(request.POST['width_support_right'])
    diameter_main_top = int(request.POST['diameter_main_top'])
    quantity_main_top = int(request.POST['quantity_main_top'])
    steel_grade_main_top = str(request.POST['steel_grade_main_top'])
    diameter_main_bottom = int(request.POST['diameter_main_bottom'])
    quantity_main_bottom = int(request.POST['quantity_main_bottom'])
    steel_grade_main_bottom = str(request.POST['steel_grade_main_bottom'])
    diameter_stirrup = int(request.POST['diameter_stirrup'])
    steel_grade_stirrup = str(request.POST['steel_grade_stirrup'])
    cover_top = int(request.POST['cover_top'])
    cover_bottom = int(request.POST['cover_bottom'])
    cover_view_left = int(request.POST['cover_view_left'])
    cover_view_right = int(request.POST['cover_view_right'])
    cover_left = int(request.POST['cover_left'])
    cover_right = int(request.POST['cover_right'])
    first_row_stirrup_range_left = int(request.POST['first_row_stirrup_range_left'])
    first_row_stirrup_range_right = int(request.POST['first_row_stirrup_range_right'])
    first_row_stirrup_spacing_left = int(request.POST['first_row_stirrup_spacing_left'])
    first_row_stirrup_spacing_right = int(request.POST['first_row_stirrup_spacing_right'])
    secondary_stirrup_spacing = int(request.POST['secondary_stirrup_spacing'])
    number_of_elements = int(request.POST['number_of_elements'])
    language = str(request.POST['language'])

    drawing = DxfElement(
        beam_span=beam_span,
        beam_height=beam_height,
        beam_width=beam_width,
        width_support_left=width_support_left,
        width_support_right=width_support_right,
        diameter_main_top=diameter_main_top,
        quantity_main_top=quantity_main_top,
        steel_grade_main_top=steel_grade_main_top,
        diameter_main_bottom=diameter_main_bottom,
        quantity_main_bottom=quantity_main_bottom,
        steel_grade_main_bottom=steel_grade_main_bottom,
        diameter_stirrup=diameter_stirrup,
        steel_grade_stirrup=steel_grade_stirrup,
        cover_view_left=cover_view_left,
        cover_view_right=cover_view_right,
        cover_bottom=cover_bottom,
        cover_top=cover_top,
        cover_left=cover_left,
        cover_right=cover_right,
        first_row_stirrup_range_left=first_row_stirrup_range_left,
        first_row_stirrup_range_right=first_row_stirrup_range_right,
        first_row_stirrup_spacing_left=first_row_stirrup_spacing_left,
        first_row_stirrup_spacing_right=first_row_stirrup_spacing_right,
        secondary_stirrup_spacing=secondary_stirrup_spacing,
        number_of_elements=number_of_elements,
        name=name,
        language=language
    )
    # dxfversion: str = 'R2010',
    # start_point_x: float = 0,
    # start_point_y: float = 0,

    filepath = f'download/Files/temp/{uuid()}.dxf'
    drawing.save(filepath)

    with open(filepath, 'rt') as dxf_file:
        response = HttpResponse(dxf_file.read())
        response['Content-Disposition'] = 'attachment; filename=' + f'{name}.dxf'
        return response
