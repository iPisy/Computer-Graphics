# Matplotlib 中的文本输出与字体设置（Windows / Python）

## 1. 如何输出文本？

使用 Matplotlib 的 `ax.text(x, y, "内容")`。其中 `x`、`y` 默认是图中的数据坐标。标题、坐标轴名称分别用 `ax.set_title()`、`ax.set_xlabel()` 和 `ax.set_ylabel()` 设置。

如果希望文字固定在绘图区的某个相对位置，而不随数据范围变化，可以加 `transform=ax.transAxes`；此时 `(0, 0)` 是绘图区左下角，`(1, 1)` 是右上角。若要把文字放在整张画布上，可使用 `fig.text(x, y, "内容")`，其默认坐标也是从 0 到 1 的相对坐标。

```python
# 示例
ax.text(0.02, 0.95, "左上角说明", transform=ax.transAxes, va="top")
```

## 2. 文本字体如何设置？

**单独设置一处文字**：在 `ax.text()` 等文字函数中传入 `fontfamily`（字体）、`fontsize`（字号，单位为点）、`fontweight`（字重）、`fontstyle`（字形）等参数。颜色可用 `color`，角度可用 `rotation`。

```python
# 示例
ax.text(1, 1, "重点", fontfamily="Microsoft YaHei",
        fontsize=18, fontweight="bold", color="red", rotation=0)
```

**设置整张图的默认字体**：在创建文字之前修改 `matplotlib.rcParams`。

```python
# 示例
import matplotlib as mpl

mpl.rcParams["font.family"] = ["Microsoft YaHei", "DejaVu Sans"]
mpl.rcParams["font.size"] = 12
```

