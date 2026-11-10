import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch
from pathlib import Path

OUT = Path(__file__).with_suffix(".png")
OUT.parent.mkdir(parents=True, exist_ok=True)

C = {  # (fond, bordure, texte)
    'ref':   ('#E8F0FB', '#3B6FB6', '#1D3B66'),
    'pivot': ('#1F3A5F', '#0F2238', '#FFFFFF'),
    'event': ('#FDF0E3', '#D9822B', '#7A3E06'),
    'refp':  ('#E7F5EC', '#2E8B57', '#14502F'),
    'off':   ('#F2F2F2', '#9E9E9E', '#6E6E6E'),
}
W, H = 2.55, 1.15
fig, ax = plt.subplots(figsize=(18, 10.5), dpi=180)
ax.set_xlim(0, 18); ax.set_ylim(-0.6, 10.3); ax.axis('off')
fig.patch.set_facecolor('white')

boxes = {}
def box(key, x, y, name, rows, pk, kind, w=W, h=H, dashed=False):
    f, b, t = C[kind]
    ax.add_patch(FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle='round,pad=0.02,rounding_size=0.12',
                                fc=f, ec=b, lw=2.2 if kind == 'pivot' else 1.6, ls='--' if dashed else '-', zorder=3))
    ax.text(x, y + 0.24, name, ha='center', va='center', fontsize=12.5 if kind != 'pivot' else 15,
            fontweight='bold', color=t, zorder=4)
    ax.text(x, y - 0.08, f'{rows} lignes', ha='center', va='center', fontsize=9.5, color=t, zorder=4)
    ax.text(x, y - 0.34, f'PK : {pk}', ha='center', va='center', fontsize=8.3, color=t, style='italic', alpha=0.9, zorder=4)
    boxes[key] = (x, y, w, h)

def edge(a, b, label, card='N–1', side_a='top', side_b='bottom', dashed=False, color='#55606E', lab_pos=0.5, arrow=True, dy=0.0):
    xa, ya, wa, ha = boxes[a]; xb, yb, wb, hb = boxes[b]
    pa = {'top': (xa, ya + ha/2), 'bottom': (xa, ya - ha/2), 'left': (xa - wa/2, ya), 'right': (xa + wa/2, ya)}[side_a]
    pb = {'top': (xb, yb + hb/2), 'bottom': (xb, yb - hb/2), 'left': (xb - wb/2, yb), 'right': (xb + wb/2, yb)}[side_b]
    ax.annotate('', xy=pb, xytext=pa, zorder=2,
                arrowprops=dict(arrowstyle='-|>' if arrow else '-', color=color, lw=1.5, ls='--' if dashed else '-',
                                mutation_scale=16, shrinkA=2, shrinkB=2))
    mx, my = pa[0] + (pb[0] - pa[0]) * lab_pos, pa[1] + (pb[1] - pa[1]) * lab_pos
    txt = f'{label}\n{card}' if card else label
    ax.text(mx, my + dy, txt, ha='center', va='center', fontsize=8.2, color='#2B2B2B', zorder=5, linespacing=1.15,
            bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='#C9CED6', lw=0.8))

# --- Référentiels machine
box('categorie', 4.5, 8.9, 'CATEGORIE', '11', 'id_categorie', 'ref')
box('classe',    9.0, 8.9, 'CLASSE', '417', 'id_classe_machine', 'ref')
box('endroit',  13.5, 8.9, 'ENDROIT', '68', 'id_endroit', 'ref')
# --- Pivot
box('machine', 9.0, 6.3, 'MACHINE', '1 649', 'id_machine_instance', 'pivot', w=3.4, h=1.3)
# --- Événements
box('reparation', 1.9, 3.3, 'REPARATION', '32 772', 'id_reparation', 'event')
box('appel',      5.5, 3.3, 'APPEL', '32 331', 'id_appel', 'event')
box('entretien',  8.7, 3.3, 'ENTRETIEN', '65 173', 'id_entretien', 'event')
box('preventif', 12.1, 3.3, 'PREVENTIF', '4 109', 'id', 'event')
box('historique', 15.5, 3.3, 'HISTORIQUE', '15 191', 'id_historique_endroit', 'event')
box('mouvement',  15.5, 0.75, 'MOUVEMENT', '15 191', 'id  (écartée)', 'off', dashed=True)
# --- Référentiels panne / action
box('nature',   0.95 + 0.4, 0.75, 'NATURE', '40', 'id_naturepanne', 'refp', w=2.25)
box('probleme', 4.0, 0.75, 'PROBLEME', '32', 'id_naturepanne', 'refp', w=2.25)
box('action',  10.4, 0.75, 'ACTION', '62', 'id_action', 'refp')

# --- Relations machine -> référentiels
edge('machine', 'categorie', 'id_categ_machine', side_a='top', side_b='bottom', lab_pos=0.55)
edge('machine', 'classe', 'id_class_machine', side_a='top', side_b='bottom', lab_pos=0.5)
edge('machine', 'endroit', 'id_endroit', side_a='top', side_b='bottom', lab_pos=0.55)
# --- Événements -> machine
for k, lp in [('reparation', 0.42), ('appel', 0.45), ('entretien', 0.45), ('preventif', 0.45), ('historique', 0.42)]:
    edge(k, 'machine', 'id_machine_instance', side_a='top', side_b='bottom', lab_pos=lp)
# --- Appel -> réparation (1-1)
edge('appel', 'reparation', 'id_reparation', card='1–1', side_a='left', side_b='right', color='#B5541C', dy=0.55)
# --- Référentiels panne / action
edge('reparation', 'nature', 'id_naturepnne', side_a='bottom', side_b='top', lab_pos=0.5)
edge('reparation', 'probleme', 'id_probleme', side_a='bottom', side_b='top', lab_pos=0.42)
edge('appel', 'probleme', 'id_problemepanne', side_a='bottom', side_b='top', lab_pos=0.55)
edge('entretien', 'action', 'id_action', side_a='bottom', side_b='top', lab_pos=0.5)
edge('preventif', 'action', 'id_action', side_a='bottom', side_b='top', lab_pos=0.5)
# --- Doublon historique / mouvement
edge('historique', 'mouvement', 'copie sans date\n(même machine,\nmême destination)', card='', side_a='bottom', side_b='top',
     dashed=True, color='#9E9E9E', arrow=False)

# --- Titre, légende, notes
ax.text(9.0, 10.15, 'Schéma relationnel retenu — Dataset ERP Maintenance', ha='center', va='center',
        fontsize=19, fontweight='bold', color='#1F3A5F')
ax.text(9.0, 9.72, 'Flèche : clé étrangère  →  clé primaire   ·   cardinalité N–1 sauf mention   ·   intégrité référentielle vérifiée : 100 %',
        ha='center', va='center', fontsize=10.5, color='#55606E')
handles = [Patch(fc=C[k][0], ec=C[k][1], label=l) for k, l in
           [('pivot', 'Table pivot'), ('ref', 'Référentiels machine'), ('event', 'Tables d\'événements (1 → N par machine)'),
            ('refp', 'Référentiels panne / action'), ('off', 'Table écartée (doublon)')]]
ax.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, -0.045), ncol=5, frameon=False, fontsize=10.5,
          handlelength=1.6, handleheight=1.1)
plt.savefig(OUT, bbox_inches='tight', facecolor='white')
print('saved', OUT)
