import plotly.express as px
import plotly.io as pio


# Writes to static folder
# Currently I store html locally for using them in web
def write_html(fig, filename):
    pio.write_html(fig, f'static/{filename}', full_html=True)


# returns filename in static folder for plot type (pie, bar, line)
# im using values like y and names like x
def plot_diagram(values, names, title, ml_predicted_values=None, additional_names=None, exclude: list = None, chart_type='pie'):
    if exclude:
        ids = [i for i, v in enumerate(names) if v not in exclude]
        names_excluded = [v for v in names if v not in exclude]
        values_new = [values[i] for i in ids]
    else:
        names_excluded = names
        values_new = values

    if chart_type == 'pie':
        fig = px.pie(names=names_excluded, values=values_new, title=title)
    elif chart_type == 'bar':
        fig = px.bar(x=names_excluded, y=values_new, title=title)
    elif chart_type == 'line':
        fig = px.line(x=names_excluded, y=values_new, title=title)
        if ml_predicted_values is not None and additional_names is not None:
            fig.add_scatter(x=additional_names, y=ml_predicted_values, mode='lines', name='ML Predicted', line=dict(color='red'))
    else:
        raise ValueError("Invalid chart_type. Supported types are 'pie', 'bar' and 'line'.")

    filename = f'{chart_type}.html'
    write_html(fig, filename)
    return filename
