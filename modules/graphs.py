"""Plotly figures for the SCAMVERSE interface.

Styling follows a restrained scheme: one hue for magnitudes, recessive grid and
axes, text in neutral ink, and colour never used as the only carrier of meaning.
"""
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go

from modules.engine import RISK_CAP, THEME_KEYWORDS

INK = "#1B1F24"
INK_2 = "#545B66"
GRID = "#E3E6EA"
ACCENT = "#1F5FA8"          # single hue for magnitude
ACCENT_FILL = "rgba(31,95,168,0.18)"
# Categorical order for the eight dimensions (validated reference palette, light mode).
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
FONT = dict(family="Source Sans Pro, Segoe UI, Arial, sans-serif", size=13, color=INK)


def _base(fig, height):
    fig.update_layout(height=height, template="simple_white", font=FONT,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=10, r=20, t=20, b=10))
    return fig


def dimension_bar(df):
    d = df.sort_values("Evidence Frequency", ascending=True)
    # colour identifies the dimension (fixed lexicon order), never its rank
    colour = {k: CATEGORICAL[i % len(CATEGORICAL)] for i, k in enumerate(THEME_KEYWORDS)}
    fig = go.Figure(go.Bar(
        x=d["Evidence Frequency"], y=d["Dimension"], orientation="h",
        marker=dict(color=[colour.get(x, ACCENT) for x in d["Dimension"]], line=dict(width=0)),
        text=[f"{v}  ({w:.1%})" for v, w in zip(d["Evidence Frequency"], d["Relative Weight"])],
        textposition="outside", textfont=dict(color=INK_2, size=12), cliponaxis=False,
        hovertemplate="%{y}<br>%{x} matches<extra></extra>"))
    _base(fig, 430)
    fig.update_xaxes(range=[0, max(d["Evidence Frequency"].max(), 1) * 1.28],
                     title_text="Lexicon matches", showgrid=True, gridcolor=GRID, zeroline=False,
                     linecolor=GRID, tickfont=dict(color=INK_2))
    fig.update_yaxes(title_text=None, linecolor=GRID, ticks="", tickfont=dict(color=INK))
    fig.update_layout(bargap=0.35)
    return fig


RADAR_LABELS = {
    "Unrealistic high return": "Unrealistic<br>return",
    "Guaranteed profit or no-risk claim": "Guaranteed /<br>no-risk claim",
    "Telegram or social media recruitment": "Social-media<br>recruitment",
    "Mule account or layered transfer": "Mule / layered<br>transfer",
    "Fake testimonial or fabricated proof": "Fake<br>testimonial",
    "Unlicensed or unclear investment entity": "Unlicensed<br>entity",
    "Crypto or cross-border laundering": "Crypto /<br>cross-border",
    "Urgency pressure": "Urgency<br>pressure",
}


def risk_radar(df):
    labels = [RADAR_LABELS.get(x, x) for x in df["Risk Indicator"]]
    theta = labels + [labels[0]]
    r = list(df["Index Contribution"]) + [df["Index Contribution"].iloc[0]]
    raw = list(df["Detected Evidence"]) + [df["Detected Evidence"].iloc[0]]
    fig = go.Figure(go.Scatterpolar(
        r=r, theta=theta, fill="toself", fillcolor=ACCENT_FILL,
        line=dict(color=ACCENT, width=2), marker=dict(size=8, color=ACCENT),
        customdata=raw, hovertemplate="%{theta}<br>contribution %{r} of " + str(RISK_CAP) +
        "<br>raw matches %{customdata}<extra></extra>"))
    _base(fig, 430)
    fig.update_layout(polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(range=[0, RISK_CAP], dtick=1, gridcolor=GRID, linecolor=GRID,
                        tickfont=dict(size=10, color=INK_2)),
        angularaxis=dict(gridcolor=GRID, linecolor=GRID, tickfont=dict(size=11, color=INK))),
        margin=dict(l=70, r=70, t=30, b=30))
    return fig


LAYOUT = {
    'SKMM/Telco': (0.0, 1.35), 'Scammer': (0.0, 0.35),
    'Telegram/Facebook': (1.0, 1.0), 'Fake Testimonial': (1.0, -0.2),
    'Victim': (2.0, 0.4), 'Public Awareness': (1.35, -0.85),
    'Mule Account': (3.0, 1.25), 'PDRM/CCID': (3.0, -0.35),
    'Bank': (4.0, 1.25), 'NSRC': (3.55, 0.45), 'SSM': (4.0, -0.35), 'Court/DPP': (4.0, -1.1),
    'BNM': (5.0, 0.45),
}


def ecosystem_network():
    nodes = ['Victim', 'Scammer', 'Telegram/Facebook', 'Fake Testimonial', 'Mule Account', 'Bank', 'BNM',
             'SSM', 'SKMM/Telco', 'NSRC', 'PDRM/CCID', 'Public Awareness', 'Court/DPP']
    edges = [('Scammer', 'Telegram/Facebook'), ('Telegram/Facebook', 'Victim'), ('Fake Testimonial', 'Victim'),
             ('Scammer', 'Fake Testimonial'), ('Victim', 'Mule Account'), ('Mule Account', 'Bank'), ('Bank', 'BNM'),
             ('Victim', 'PDRM/CCID'), ('PDRM/CCID', 'NSRC'), ('PDRM/CCID', 'SSM'), ('PDRM/CCID', 'BNM'),
             ('PDRM/CCID', 'Court/DPP'), ('NSRC', 'Bank'), ('SKMM/Telco', 'Telegram/Facebook'),
             ('Public Awareness', 'Victim'), ('BNM', 'Bank')]
    # Actor roles: shape + grey level carry the role, so it never relies on colour alone.
    role = {'Scammer': 'offender', 'Telegram/Facebook': 'offender', 'Fake Testimonial': 'offender',
            'Mule Account': 'offender', 'Victim': 'victim'}
    style = {'offender': dict(symbol='diamond', color='#B23A3A', name='Offender channel'),
             'victim': dict(symbol='circle', color='#1B1F24', name='Victim'),
             'institution': dict(symbol='square', color=ACCENT, name='Institution / prevention')}
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    pos = LAYOUT  # fixed layered layout: offender side (left) to institutional side (right)
    fig = go.Figure()
    for a, b in G.edges():
        x0, y0 = pos[a]; x1, y1 = pos[b]
        fig.add_annotation(x=x1, y=y1, ax=x0, ay=y0, xref='x', yref='y', axref='x', ayref='y',
                           showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=1.3,
                           arrowcolor='#8A919C', standoff=12, startstandoff=12, text='')
    for key, st in style.items():
        members = [n for n in G.nodes() if role.get(n, 'institution') == key]
        fig.add_trace(go.Scatter(
            x=[pos[n][0] for n in members], y=[pos[n][1] for n in members], mode='markers',
            text=members, name=st['name'],
            marker=dict(size=18, symbol=st['symbol'], color=st['color'], line=dict(width=1.5, color='white')),
            hovertemplate='%{text}<extra></extra>'))
    # Node labels as annotations with a white backing so edges never run through the text.
    for n in G.nodes():
        fig.add_annotation(x=pos[n][0], y=pos[n][1], text=n, showarrow=False, yshift=-22,
                           font=dict(color=INK, size=12), bgcolor='rgba(255,255,255,0.92)', borderpad=1)
    _base(fig, 560)
    fig.update_layout(xaxis=dict(visible=False, range=[-0.45, 5.45]), yaxis=dict(visible=False, range=[-1.45, 1.6]),
                      legend=dict(orientation='h', y=-0.02, x=0, font=dict(color=INK)))
    return fig


def sunburst(df):
    temp = df[df["Evidence Frequency"] > 0].copy()
    temp['Root'] = 'Scam ecosystem'
    # colour follows the dimension (fixed lexicon order), never its rank
    colour = {d: CATEGORICAL[i % len(CATEGORICAL)] for i, d in enumerate(THEME_KEYWORDS)}
    fig = px.sunburst(temp, path=['Root', 'Dimension'], values='Evidence Frequency',
                      color='Dimension', color_discrete_map={**colour, '(?)': '#FFFFFF'})
    fig.update_traces(marker=dict(line=dict(color='white', width=2)), insidetextfont=dict(color=INK, size=12),
                      hovertemplate='%{label}<br>%{value} matches<extra></extra>')
    _base(fig, 520)
    return fig
