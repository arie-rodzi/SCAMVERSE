import networkx as nx
import plotly.graph_objects as go
import plotly.express as px

def dimension_bar(df):
    fig = px.bar(df, x='Evidence Frequency', y='Dimension', orientation='h', text='Evidence Frequency', color='Relative Weight', color_continuous_scale='Turbo')
    fig.update_layout(height=470, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', margin=dict(l=10,r=10,t=20,b=10))
    return fig

def risk_radar(df):
    fig = go.Figure(data=go.Scatterpolar(r=df['Detected Evidence'].clip(upper=6), theta=df['Risk Indicator'], fill='toself'))
    fig.update_layout(height=470, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', polar=dict(bgcolor='rgba(15,23,42,.45)'))
    return fig

def ecosystem_network():
    nodes = ['Victim','Scammer','Telegram/Facebook','Fake Testimonial','Mule Account','Bank','BNM','SSM','SKMM/Telco','NSRC','PDRM/CCID','Public Awareness','Court/DPP']
    edges = [('Scammer','Telegram/Facebook'),('Telegram/Facebook','Victim'),('Fake Testimonial','Victim'),('Scammer','Fake Testimonial'),('Victim','Mule Account'),('Mule Account','Bank'),('Bank','BNM'),('Victim','PDRM/CCID'),('PDRM/CCID','NSRC'),('PDRM/CCID','SSM'),('PDRM/CCID','BNM'),('PDRM/CCID','Court/DPP'),('NSRC','Bank'),('SKMM/Telco','Telegram/Facebook'),('Public Awareness','Victim'),('BNM','Banks')]
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from([e for e in edges if e[0] in nodes and e[1] in nodes])
    pos = nx.spring_layout(G, seed=12, k=0.85)
    edge_x, edge_y = [], []
    for a,b in G.edges():
        x0,y0 = pos[a]; x1,y1 = pos[b]
        edge_x += [x0,x1,None]; edge_y += [y0,y1,None]
    node_x,node_y,labels = [],[],[]
    for n in G.nodes():
        x,y = pos[n]; node_x.append(x); node_y.append(y); labels.append(n)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=1.8, color='rgba(148,163,184,.7)'), hoverinfo='none'))
    fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='markers+text', text=labels, textposition='top center', marker=dict(size=30, color=list(range(len(labels))), colorscale='Turbo', line=dict(width=2, color='white')), textfont=dict(color='white', size=12), hoverinfo='text'))
    fig.update_layout(height=650, margin=dict(l=10,r=10,t=20,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
    return fig

def sunburst(df):
    temp = df.copy()
    temp['Root'] = 'Online Investment Scam Ecosystem'
    fig = px.sunburst(temp, path=['Root','Dimension'], values='Evidence Frequency', color='Relative Weight', color_continuous_scale='Turbo')
    fig.update_layout(height=560, paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    return fig
