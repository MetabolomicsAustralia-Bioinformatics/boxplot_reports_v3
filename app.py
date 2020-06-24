from flask import Flask, Response, request, render_template, make_response, redirect, url_for, flash
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.backends.backend_pdf import PdfPages

import io
import csv
import numpy as np
import pandas as pd
import boxplot_utils as bxu

import time
import secrets

app = Flask(__name__)
app.config["CLIENT_DIR"] = "/Users/don/Documents/flask_boxplot_reports_v3/static/client"


@app.route("/", methods=['POST', 'GET'])
def boxplot_report():
    return render_template("boxplot_report.html")


@app.route('/transform', methods=["GET", "POST"])
def transform_view():
    """ renders the plot on the fly.
    """
    f = request.files['input_file']
    if not f:
        return "Main input file not found!"

    # Read uploaded data as a Stream into a dataframe. 
    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)
    contents = []
    for row in csv_input:
        contents.append(row)
    d0 = pd.DataFrame(data=contents[1:], columns=contents[0])

    # define some variables
    sample_name_col = d0.columns[0]
    grp_name_col = d0.columns[1]
    metabs_ls = list(d0.columns)[2:]
    metabs_ls.sort()
    reordered_metabs_ls = list(d0.columns)[:2] + metabs_ls
    group_colname = list(d0.columns)[1]
    groups_ls = list(set(d0[group_colname]))
    # Convert the appropriate columns to numeric
    d0[metabs_ls] = d0[metabs_ls].apply(pd.to_numeric)

    print("Num. metabs = %s" % len(metabs_ls))
    batches_ls = bxu.batch_metabs(metabs_ls, batch_size=30)
    print("Grouping into %s batches: first %s of size 30, last of size %s" % (len(batches_ls), len(batches_ls)-1, len(batches_ls[-1])))

    # Set some plot params
    matplotlib.rc('axes',edgecolor='grey')
    title_fontsize=16
    # colours_ls corresponds to colorbrewer's qualitative 7-class Set3
    colours_ls = ["#8dd3c7", "#bebada", "#fb8072", 
    "#ffffb3", "#80b1d3", "#fdb462", 
    "#fdb462", "#b3de69"]

    # Start plotting loop
    # Start plotting loop
    t0 = time.time()
    figs_ls = []

    batch_counter = 0 # Used for print() purposes only
    for batch in batches_ls:
        num_cols = 5
        num_rows = 6
        
        # Adjust num_rows and num_cols for the last batch as necessary
        if len(batch) < (num_cols * num_rows):
            if divmod(len(batch), num_cols)[1] > 0: # If there's a remainder
                num_rows = divmod(len(batches_ls[-1]), num_cols)[0] + 1
            else: # if the last batch so happens to be a multipe of num_cols (5)
                num_rows = divmod(len(batches_ls[-1]), num_cols)[0]
        print("batch %s: len(batch) = %s, num_rows = %s, num_cols = %s" % (batch_counter, len(batch), num_rows, num_cols))
        
        # plot!
        fig, axarr = plt.subplots(num_rows, num_cols, figsize=(20, 4.5*num_rows), sharex='col')

        idx = 0
        for i in np.arange(num_rows):
            for j in np.arange(num_cols):
                # Continue to proc if this is NOT the last batch
                # OR if is it, check that idx < len(last_batch), 
                # because last_batch[idx] will throw an index-out-of-bounds error
                if (len(batch) == 30) or ((len(batch) < 30) and (idx < len(batch))):
                    plot_input_arr = bxu.get_bplot_inputs(d0, groups_ls, batch[idx], group_colname=grp_name_col)
                    
                    # See note above on why num_rows > 1 and num_rows == 1 need different treatment
                    if num_rows > 1:
                        axarr[i, j].set_title(batch[idx], fontsize=title_fontsize)
                        bplot = axarr[i, j].boxplot(plot_input_arr, 
                                                    patch_artist=True, 
                                                    widths=tuple([0.85]*len(groups_ls)),
                                                    labels=groups_ls, 
                                                    showfliers=False, 
                                                    zorder=10)

                        # Manually add scatterplot of datapoints
                        for grp_idx in range(len(groups_ls)):
                            scatter_y = plot_input_arr[grp_idx]
                            scatter_x = np.random.normal(grp_idx+1, 0.04, size=len(scatter_y))
                            axarr[i, j].scatter(scatter_x, scatter_y, c="black", zorder=11, alpha=0.7)
                            
                        # Add bg colour on odd rows
                        if i%2 == 0:
                            axarr[i, j].set_facecolor('#EAF2F6')
                            
                        # Add grid
                        axarr[i, j].grid(True)
                        
                    elif num_rows == 1:
                        axarr[j].set_title(batch[idx], fontsize=title_fontsize)
                        bplot = axarr[j].boxplot(plot_input_arr, 
                                                patch_artist=True, 
                                                widths=tuple([0.85]*len(groups_ls)),
                                                labels=groups_ls, 
                                                showfliers=False, 
                                                zorder=10)

                        # Manually add scatterplot of datapoints
                        for grp_idx in range(len(groups_ls)):
                            scatter_y = plot_input_arr[grp_idx]
                            scatter_x = np.random.normal(grp_idx+1, 0.04, size=len(scatter_y))
                            axarr[j].scatter(scatter_x, scatter_y, c="black", zorder=11, alpha=0.7)
                            
                        # Add grid
                        axarr[j].grid(True)

                    # Aesthetics
                    for box_idx in range(len(bplot['boxes'])):
                        bplot['medians'][box_idx].set_color('black')
                        bplot['boxes'][box_idx].set(linewidth=1.5)

                    idx += 1
                    # colour in boxplots
                    for patch, color in zip(bplot['boxes'], colours_ls):
                        patch.set_facecolor(color)

        fig.subplots_adjust(wspace=0.125, hspace=0.12)
        figs_ls.append(fig)
        plt.close()

        batch_counter +=1

    #fig.savefig("test.pdf", bbox_inches='tight')
    print("Done in %.2fs" % (time.time() - t0))

    # write out boxplots in a multi-page pdf
    fn = f"boxplots-{secrets.token_hex(nbytes=10)}.pdf"
    pdf = matplotlib.backends.backend_pdf.PdfPages(app.config["CLIENT_DIR"] + "/" + fn)
    for fig in figs_ls:
        pdf.savefig(fig, bbox_inches = 'tight')
    pdf.close()

    return redirect(url_for("boxplot_report"))
    #return send_file('./tmp/output3.pdf', attachment_filename='output3.pdf')


if __name__ == "__main__":
    app.run(debug=True)
