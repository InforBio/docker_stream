"""Patch STREAM's extra.py for pandas compatibility.

Newer pandas rejects assigning an iterable to a single cell via .loc.
Fix: use .at for single-cell writes and a per-cell loop for multi-column assignments.
"""

fp = '/opt/miniconda/envs/stream_env/lib/python3.7/site-packages/stream/extra.py'
c = open(fp).read()

# line ~929: per-edge tuple assignment -> per-cell .at loop
c = c.replace(
    "df_stream.loc[df_stream.index[id_cells],'edge'] = [x]",
    "for _idx in df_stream.index[id_cells]: df_stream.at[_idx,'edge'] = x")

# single-cell 'boundary' / 'edge' column assignments: .loc -> .at
c = c.replace("df_bins.loc['boundary',\"win\"", "df_bins.at['boundary',\"win\"")
c = c.replace("df_bins.loc['edge',\"win\"",     "df_bins.at['edge',\"win\"")

# multi-column edge assignment on one row -> per-column .at loop
c = c.replace(
    'df_bins.loc[\'edge\',[\"win\"+str(total_bins+i_win) for i_win in range(mat_w.shape[0])]] = [[edge_i]]',
    'for _w in [\"win\"+str(total_bins+i_win) for i_win in range(mat_w.shape[0])]: df_bins.at[\'edge\',_w] = [edge_i]')

open(fp, 'w').write(c)
print('extra.py patched successfully')
