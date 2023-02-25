from __future__ import annotations
import calendar
import tempfile
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
import os
import sys
import mvexperiment.experiment as experiment
import numpy as np
import zipfile
import matplotlib.pyplot as plt
import pandas as pd
import json
import shutil
import altair as alt
import nanodata
import nanodata.nanodata as nano
from NanoPrepare import save_uploaded_file, base_chart, layer_charts
import nanoanalysisdata.engine as engine
import nanoanalysisdata.motor as motor

def refill(collection):
    for i in range(len(collection)):
        c = engine.haystack[i]
        try:
            collection[i].set_XY(c._Z * 1e9, c._F * 1e9)
        except IndexError:
            print("IndexError")
    # filter method
    # self.fmethod_changed()


def numbers():
    E_array = []
    F_data = []
    ind_data = []

    for c in motor.collection:
        if c.active is True and c.E is not None:
            E_array.append(c.E)
            # Average Hertz
            F_data.append(c.touch)
            ind_data.append(c.ind)
    # if len(E_array) < 2:
    #     self.ui.data_average.setText('0.00')
    #     self.ui.data_std.setText('0.00')
    #     self.es_average.setData(None)
    #     self.indentation_fit.setData(None)
    #     self.indentation_fit_avg.setData(None)
    #     self.es_averageZoom.setData(None)
    #     self.es_averageFit.setData(None)
    #     self.fdistance_fit.setData(None)
    #     return

    eall = np.array(E_array)
    val = str(int(np.average(eall) / 10) / 100.0)
    try:
        err = str(int(np.std(eall) / 10) / 100.0)
    except:
        err = 0
    # self.ui.data_average.setText(
    #     '<span>{}&plusmn;{}</span>'.format(val, err))
    # self.Yav = str(int(np.average(eall)))
    # self.Yav_std = str(int(np.std(eall)))
    bins = 'auto'
    y, x = np.histogram(eall, bins=bins, density=True)
    print("y ", y)
    # if len(y) >= 3:
    #     try:
    #         x0, w, A, nx, ny = motor.gauss_fit(x, y)
    #         x, y, z = motor.calc_hertz(x0, self.collection[0].R, self.collection[0].k, float(
    #             self.ui.fit_indentation.value()))
    #         self.indentation_fit.setData(x, y)
    #         self.indentation_fit_avg.setData(x, y)
    #         self.fdistance_fit.setData(z, y)
    #     except:
    #         self.indentation_fit.setData(None)
    #         self.fdistance_fit.setData(None)
    #         self.indentation_fit_avg.setData(None)
    #     try:
    #         x_hertz, y_hertz, er_hertz = motor.getMedCurve(
    #             ind_data, F_data, error=True)
    #         self.hertz_average_error = er_hertz
    #     except TypeError:
    #         return
    #     except ValueError:
    #         return
    #     # Setting average hertz data
    #     if self.ui.analysis.isChecked() is True:
    #         print("************")
    #         indmax = float(self.ui.fit_indentation.value())
    #         self.x_hertz_average = x_hertz
    #         self.y_hertz_average = y_hertz
    #         self.hertz_average.setData(x_hertz, y_hertz)
    #         # jmax_hertz = np.argmin((x_hertz-indmax)**2)
    #         self.hertz_average.setData(x_hertz, y_hertz)
    #         self.hertz_average_top.setData(x_hertz, (y_hertz + er_hertz / 2))
    #         self.hertz_average_bottom.setData(
    #             x_hertz, (y_hertz - er_hertz / 2))
    #     else:
    #         self.hertz_average.setData(None)
    #         self.hertz_average_top.setData(None)
    #         self.hertz_average_bottom.setData(None)

    # Elasticity Spectra
    # if self.ui.es_analysis.isChecked() is True:
    #     E_data_x = []
    #     E_data_y = []
    #     Radius = []
    #     for c in self.collection:
    #         if c.active is True and c.E is not None:
    #             # Elasticity Spectra
    #             Radius.append(c.R)
    #             E_data_x.append(c.Ex)  # contact radius
    #             E_data_y.append(c.Ey)
    #     try:
    #         x, y, er = motor.getMedCurve(E_data_x, E_data_y, error=True)
    #         self.es_average_error = er * 1e9
    #     except TypeError:
    #         return
    #     except ValueError:
    #         return
    #
    #
    #     x = x ** 2 / np.average(Radius)  # ind
    #     self.es_average.setData(x, y * 1e9)  # E vs ind
    #     self.ES_array_x = x
    #     self.ES_array_y = y * 1e9
    #     indmax = float(self.ui.fit_indentation.value())
    #     # rmax = np.sqrt(indmax * np.average(Radius))
    #     jmax = np.argmin((x - indmax) ** 2)
    #
    #     # Setting average elasticity spectra data
    #     self.es_top.setData(x[:jmax], (y[:jmax] + er[:jmax] / 2) * 1e9)
    #     self.es_bottom.setData(x[:jmax], (y[:jmax] - er[:jmax] / 2) * 1e9)
    #     self.es_averageZoom.setData(x[:jmax], y[:jmax] * 1e9)
    #     all = motor.fitExpSimple(np.sqrt(x[:jmax] * np.average(Radius)), y[:jmax], er[:jmax])
    #     if all is not None:
    #         self.es_averageFit.setData(
    #             x[:jmax], motor.TheExp(np.sqrt(x[:jmax] * np.average(Radius)), *all[0]) * 1e9)
    #         val = str(int((all[0][0] * 1e9) / 10) / 100.0)
    #         try:
    #             err = str(int((all[1][0] * 1e9) / 10) / 100.0)
    #             self.ui.decay_e0.setText(
    #                 '<span>{}&plusmn;{}</span>'.format(val, err))
    #         except OverflowError:
    #             err = 0
    #             self.ui.decay_e0.setText(
    #                 '<span>{}&plusmn;{}</span>'.format(val, 'XXX'))
    #         self.E0 = str(int(all[0][0] * 1e9))
    #         self.E0_std = str(int(all[1][0] * 1e9))
    #         val = str(int((all[0][1] * 1e9)))
    #         try:
    #             err = str(int((all[1][1] * 1e9)))
    #             self.ui.decay_eb.setText(
    #                 '<span>{}&plusmn;{}</span>'.format(val, err))
    #         except OverflowError:
    #             err = 0
    #             self.ui.decay_eb.setText(
    #                 '<span>{}&plusmn;{}</span>'.format(val, 'XXX'))
    #         self.Eb = str(int(all[0][1] * 1e9))
    #         self.Eb_std = str(int(all[1][1] * 1e9))
    #         val = str(int((all[0][2])))
    #         try:
    #             err = str(int((all[1][2])))
    #             self.ui.decay_d0.setText(
    #                 '<span>{}&plusmn;{}</span>'.format(val, err))
    #         except OverflowError:
    #             self.ui.decay_d0.setText(
    #                 '<span>{}&plusmn;{}</span>'.format(val, 'XXX'))
    #         self.d0 = str(int(all[0][2]))
    #         self.d0_std = str(int(all[1][2]))
    #
    #     eall = y[:jmax]
    #     val = str(int(np.average(eall * 1e9) / 10) / 100.0)
    #     err = str(int(np.std(eall * 1e9) / 10) / 100.0)
    #     self.ui.data_std.setText('<span>{}&plusmn;{}</span>'.format(val, err))
    #     self.ESav = str(int(np.average(eall * 1e9)))
    #     self.ESav_std = str(int(np.std(eall * 1e9)))
    # else:
    #     try:
    #         self.es_top.setData(None)
    #         self.es_bottom.setData(None)
    #         self.es_averageZoom.setData(None)
    #         self.es_averageFit.setData(None)
    #         self.es_average.setData(None)
    #         self.ui.data_std.setText('0.00')
    #         self.ui.decay_e0.setText('0.00')
    #         self.ui.decay_d0.setText('0.00')
    #         self.ui.decay_eb.setText('0.00')
    #
    #     except:
    #         pass

def count():
    Ne = 0
    Na = 0
    Ni = 0
    for c in motor.collection:
        if c.active is True:
            Na += 1
        elif c.included is False:
            Ne += 1
        else:
            Ni += 1
    # self.ui.stats_ne.setText(str(Ne))
    # self.ui.stats_ni.setText(str(Ni))
    # self.ui.stats_na.setText(str(Na))
    # self.Na = str(Na)
    numbers()

def hertz_changed():
    for c in motor.collection:
        c.filter_all(False, check_active=True)  # False does not re-compute contact point
    count()

def handle_click(i: int) -> None:
    # activate and deactivate curve in haystack on checkbox click
    if engine.haystack[i].active:
        engine.haystack[i].active = False
    else:
        engine.haystack[i].active = True

def generate_raw_curves(haystack: list) -> list:
    all_curves = []
    for curve in haystack:
        if curve.active:
            df = pd.DataFrame(
                {
                    "z": curve.data["Z"],
                    "f": curve.data["F"],
                }
            )
            all_curves.append(df)
    return all_curves



def main() -> None:
    st.set_page_config(
        layout="wide", page_title="NanoWeb", page_icon="/images/cellmech.png"
    )
    top_bar = st.container()
    file = top_bar.file_uploader("Upload a JSON file")
    curve_expander = st.expander("Curve selection")
    graph_bar = st.container()
    graph_first_col, graph_third_col, graph_fourth_col = graph_bar.columns(3)

    filter_bar = st.container()
    filter_bar.write("Global Config")
    filter_first_col, filter_second_col, filter_third_col, filter_fourth_col, filter_fifth_col = filter_bar.columns(5)

    if file is not None:
        if file.name.endswith(".json"):
            save_uploaded_file(file, "data")

            # Load the JSON file
            f = open("data/" + file.name, "r")
            structure = json.load(f)
            # st.write(structure)

            for cv in structure["curves"]:
                engine.haystack.append(engine.curve(cv))
                motor.collection.append(motor.Nanoment(engine.curve(cv)))

            refill(motor.collection)

            # for c in engine.haystack:
            #     node = motor.Nanoment(c)
            #     # node.setCPFunction(self.contactPoint.calculate)
            #     # node.connect(self, c.myTree)
            #     # c.myTree.nano = node
            #     collection.append(node)

            # File selection checkboxes
            #graph_first_col.write("Files")
            #create a checkbox for each file in the haystack
            for i, curve in enumerate(engine.haystack):
                curve_expander.checkbox(curve.filename, key=i, on_change=handle_click, args=(i,))

            # Raw curve plot
            graph_first_col_raw = graph_first_col.container()
            graph_first_col_raw.write("Raw curves")
            graph_first_col_raw_plot = graph_first_col_raw.line_chart()
            raw_curves = generate_raw_curves(engine.haystack)

            graph_first_col_raw_plot.altair_chart(
                layer_charts(raw_curves, base_chart),
                use_container_width=True
            )

            # Current curve plot
            graph_first_col_current = graph_first_col.container()
            graph_first_col_current.write("Current curve")
            options = [curve.filename for curve in engine.haystack if curve.active]
            selected_index = options.index(graph_first_col_current.selectbox('Select a curve', options, index=0))
            graph_first_current_plot = graph_first_col_current.line_chart()

            graph_first_current_plot.altair_chart(
                base_chart(raw_curves[selected_index]),
                use_container_width=True
            )

            # Hertz analysis
            hertz_active = graph_third_col.checkbox("Hertz Analysis")

            if hertz_active:
                hertz_changed()
            #     graph_third_col_indent = graph_third_col.container()
            #     graph_third_col_indent.write("Indentation curves")
            #     graph_third_col_indent_plot = graph_third_col_indent.line_chart()
            #
            #     graph_third_col_f_ind = graph_third_col.container()
            #     graph_third_col_f_ind.write("Average F-ind")
            #     graph_third_col_f_ind_plot = graph_third_col_f_ind.line_chart()
            #
            #     graph_third_col_elasticity = graph_third_col.container()
            #     graph_third_col_elasticity.write("Elasticity values")
            #     graph_third_col_elasticity_plot = graph_third_col_elasticity.line_chart()

            # Elasticity Spectra analysis
            el_spec_active = graph_fourth_col.checkbox("Elasticity Spectra Analysis")
            if el_spec_active:
                graph_fourth_col_el_spec = graph_fourth_col.container()
                graph_fourth_col_el_spec.write("Elasticity Spectra")
                graph_fourth_col_el_spec_plot = graph_fourth_col_el_spec.line_chart()

                graph_fourth_col_bilayer = graph_fourth_col.container()
                graph_fourth_col_bilayer.write("Bilayer model")
                graph_fourth_col_bilayer_plot = graph_fourth_col_bilayer.line_chart()

        else:
            st.warning("Only files with the .json extension are supported.")


if __name__ == "__main__":
    main()


# figure out why its not working
# make it work
# Celebrate
# Go to bed
