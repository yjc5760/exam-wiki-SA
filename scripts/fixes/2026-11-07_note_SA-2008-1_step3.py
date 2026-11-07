"""SA-2008-1 表述修正（非勘誤）：§4 步驟 3 刪除錯誤的單位力推導、§5 零桿敘述改寫。可重複執行。"""
from pathlib import Path
p = Path(__file__).resolve().parents[2] / "raw/solutions/SA-2008-1/SA-2008-1.md"
t = p.read_text(encoding="utf-8")
a = t.index("### 步驟 3：計算單位虛力內力")
b = t.index("### 步驟 4：變形相容條件與求贅力")
new3 = r"""### 步驟 3：計算單位虛力內力 $u$ (Primary Structure with $X=1$)
於 D 點施加向右 $X=1$，無其他外載。
- **整體平衡**（先對 E 取矩，再用整體力矩對 A 複核）：
  $\Sigma M_E = 0 \implies A_y(0-20) - 1\times(10-0) = 0 \implies A_y = -0.5\ (\downarrow)$
  $\Sigma F_y = 0 \implies A_y + E_y = 0 \implies E_y = 0.5\ (\uparrow)$
  $\Sigma F_x = 0 \implies 1 + E_x = 0 \implies E_x = -1\ (\leftarrow)$
  複核 $\Sigma M_A = E_y\times 20 - 1\times 10 = 10 - 10 = 0$ ✓
- **節點 A**：
  $\Sigma F_y = 0 \implies u_{AB}\times\frac{1}{\sqrt{5}} + A_y = 0 \implies u_{AB} = 0.5\sqrt{5}$
  $\Sigma F_x = 0 \implies u_{AC} + u_{AB}\times\frac{2}{\sqrt{5}} = 0 \implies u_{AC} = -1$
- **節點 C**：$u_{CE} = u_{AC} = -1$，$u_{BC} = 0$（C 點無垂直力）。
- **節點 D**：
  $\Sigma F_x = 0 \implies 1 - u_{BD}\times\frac{2}{\sqrt{5}} = 0 \implies u_{BD} = \frac{\sqrt{5}}{2}$
  $\Sigma F_y = 0 \implies -u_{DE} - u_{BD}\times\frac{1}{\sqrt{5}} = 0 \implies u_{DE} = -0.5$
- **節點 E**（檢核）：
  $\Sigma F_x = 0 \implies -u_{CE} - u_{BE}\times\frac{2}{\sqrt{5}} + E_x = 1 - u_{BE}\times\frac{2}{\sqrt{5}} - 1 = 0 \implies u_{BE} = 0$
  $\Sigma F_y = u_{BE}\times\frac{1}{\sqrt{5}} + u_{DE} + E_y = 0 - 0.5 + 0.5 = 0$ ✓

彙整：$A_y = -0.5$、$E_y = 0.5$、$E_x = -1$；$u_{AB} = u_{BD} = \frac{\sqrt{5}}{2}$、$u_{AC} = u_{CE} = -1$、$u_{BC} = u_{BE} = 0$、$u_{DE} = -0.5$。

"""
if "（先對 E 取矩，再用整體力矩對 A 複核）" not in t:
    t = t[:a] + new3 + t[b:]
old5 = "- **無載桿（零桿）的物理意義**：$BC$ 桿在此載重下為絕對的零桿（不受外載且未做為贅力受力點），這在實務上稱為**穩定桿**。它的存在雖然對承擔 $10\\text{ kN}$ 的重力沒有直接貢獻，但能防止長柱屈曲並維持桁架整體幾何形狀穩定。"
new5 = "- **零桿 BC**：C 點只有 AC、CE 兩根水平桿與垂直桿 BC，且 C 點無外力，垂直平衡直接得 $F_{BC} = 0$（基本結構與單位力狀態皆然，故最終也為 0）。BC 在本載重下不受力，但仍是幾何上必要的桿件：拿掉它，C 點在垂直方向失去約束，桁架變成機構。\n- **D 支承受拉**：最終 $D_x = 6.734\\text{ kN}$ 向右，表示右側牆對 D 是拉力。本解照題目把滾支承視為雙向約束；若支承只能受壓，D 會脫離牆面，需改以 $D_x = 0$ 重算。"
if old5 in t:
    t = t.replace(old5, new5)
foot = "*修正日期：2026-11-07（非勘誤）表述修正：§4 步驟 3 刪除錯誤的單位力推導與自我更正註記、只留正確推導並加整體力矩複核；§5 零桿 BC 敘述改寫、補 D 支承受拉說明；答案不變*"
if foot not in t:
    t = t.rstrip("\n") + "\n" + foot + "\n"
p.write_text(t, encoding="utf-8")
print("ok")
