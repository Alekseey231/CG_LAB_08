from typing import List, Union

from PyQt5.QtCore import QPoint
from sympy import Point, Polygon


NOT_VISIBLE = 1


def otsek_all(all_line_segment: List[List[QPoint]], polygon: List[QPoint]):
    all_line_segment_visible = []
    # print(all_line_segment)
    # print(polygon)
    if not is_correct_polygon(polygon):
        return -1
    for line_segment in all_line_segment:
        result = otsek(line_segment, polygon)
        all_line_segment_visible.append(result)
        # print(1111)
    return all_line_segment_visible


def rotate(A: QPoint, B: QPoint, C: QPoint):
    return (B.x() - A.x()) * (C.y() - B.y()) - (B.y() - A.y()) * (C.x() - B.x())


def is_correct_polygon(polygon: List[QPoint]):
    try:
        p = [[point.x(), point.y()] for point in polygon]
        poly = Polygon(*p)
        return poly.is_convex()
    except Exception as e:
        print(e)


def otsek(vector: List[QPoint], polygon: List[QPoint]):
    t_start: float = 0
    t_end: float = 1
    P1, P2 = vector
    D: QPoint = P2 - P1

    signed = sign(rotate(polygon[0], polygon[1], polygon[2]))
    c_x = signed
    c_y = -c_x

    for i in range(len(polygon) - 1):
        f: QPoint = polygon[i]
        side: QPoint = polygon[i + 1] - polygon[i]
        n: QPoint = QPoint(c_y * side.y(), c_x * side.x())
        w: QPoint = P1 - f
        D_ck: float = scalar(n, D)
        #print(polygon[i + 1], polygon[i], n)
        # print("D_CK", D_ck)
        W_ck: float = scalar(n, w)
        if D_ck == 0:
            if W_ck >= 0:
                continue
            else:
                return NOT_VISIBLE
        t = -W_ck / D_ck
        # print(t)
        if D_ck > 0:
            #print(">0", t)
            if t > 1:
                return NOT_VISIBLE
            else:
                t_start = max(t_start, t)
        else:
            #print("<=0", t)
            if t < 0:
                return NOT_VISIBLE
            else:
                t_end = min(t_end, t)
    #print(t_start, t_end)
    if t_start <= t_end:
        start = P1 + D * t_start
        end = P1 + D * t_end
        #start = QPoint(round(P1.x() + D.x() * t_start), round(P1.y() + D.y() * t_start))
        #end = QPoint(round(P1.x() + D.x() * t_end), round(P1.y() + D.y() * t_end))
        return start, end
    else:
        return NOT_VISIBLE


def scalar(a: QPoint, b: QPoint) -> float:
    # print("Scalar ", a, b)
    res = a.x() * b.x() + a.y() * b.y()
    # print("Res ", res)
    return res


def sign(x: float) -> int:
    ret = 0
    if x > 0:
        ret = 1
    elif x < 0:
        ret = -1
    return ret


def brezenhem_int(start_point: QPoint, end_point: QPoint, is_step: bool = False) -> Union[list, int]:
    pointed_list = []
    steps = 0

    if start_point == end_point:
        pointed_list.append([start_point.x(), start_point.y()])
    else:
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()

        sign_x = sign(dx)
        sign_y = sign(dy)

        dx = abs(dx)
        dy = abs(dy)

        is_swap = 0

        if dy > dx:
            dy, dx = dx, dy
            is_swap = 1

        error = 2 * dy - dx

        x0 = start_point.x()
        y0 = start_point.y()

        old_x = x0
        old_y = y0

        for i in range(0, int(dx) + 1):
            pointed_list.append([x0, y0])

            if error >= 0:
                if is_swap:
                    x0 += sign_x
                else:
                    y0 += sign_y
                error -= 2 * dx

            if error <= 0:
                if is_swap:
                    y0 += sign_y
                else:
                    x0 += sign_x
                error += 2 * dy

            if is_step and old_x != x0 and old_y != y0:
                steps += 1
            old_x = x0
            old_y = y0

    if is_step:
        return steps

    return pointed_list
