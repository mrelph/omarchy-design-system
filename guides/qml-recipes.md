# QML recipes (copy-paste, theme-safe)

```qml
import QtQuick
import qs.Commons   // Color, Style, Border, Util
import qs.Ui        // Button, Toggle, Panel, CursorSurface, ...
```

## Colors — always roles
```qml
color: Color.popups.background                     // surface
color: Color.foreground                            // text
color: Qt.darker(Color.foreground, 1.4)            // dim text (light-safe)
color: Util.alpha(Color.foreground, 0.12)          // separator
color: Style.hoverFillFor(Color.foreground, Color.accent)   // state fill
color: Color.urgent                                // attention only
```

## Bordered surface (theme gradient aware)
```qml
BorderSurface {
  radius: Style.cornerRadius
  color: Color.popups.background
  borderSpec: Border.surfaceSpec("popups", "border", Color.popups.border, Math.max(1, Style.space(2)))
  padding: Style.spacing.panelPadding
}
```

## Control chrome ladder (focus > hot > normal)
```qml
Rectangle {
  readonly property bool hot: hover.hovered || hasCursor
  color:        Style.controlFill(activeFocus, hot, Color.foreground, Color.accent)
  border.color: Style.controlBorder(activeFocus, hot, Color.foreground, Color.accent)
  border.width: Style.controlBorderWidth(activeFocus, hot)
  radius: Style.cornerRadius
}
```

## Typography
```qml
Text { font.family: Style.font.family; font.pixelSize: Style.font.body }
PanelSectionHeader { text: "Wi-Fi networks" }      // caption + letterSpacing 1
```

## Spacing
```qml
spacing: Style.spacing.rowGap
Layout.leftMargin: Style.spacing.rowPaddingX
implicitWidth: Style.space(380)                    // legacy px, scaled
```

## Bar widget + panel skeleton
```qml
// BarWidget.qml
BarWidget {
  id: root; moduleName: "you.thing"
  Loader { id: panelLoader; source: "Panel.qml"; onLoaded: { item.bar = root.bar; item.settings = root.settings; item.anchorItem = button; item.hostWidget = root } }
  BarIconButton { id: button; anchors.fill: parent; bar: root.bar; text: "󰖙"; slotSize: Style.bar.statusSlot; tooltipText: ""
    onPressed: function(b) { if (b === Qt.LeftButton) panelLoader.item.toggle(); else if (b === Qt.MiddleButton) panelLoader.item.refresh() } }
}
// Panel.qml
Panel {
  id: root; moduleName: "you.thing"; ipcTarget: "you.thing"; manageIpc: false
  property var anchorItem: null; property var hostWidget: null
  // copy the cursor model (focusSection/selectedIndex/moveCursor/...) verbatim from
  // /usr/share/omarchy/shell/plugins/dev-gallery/GalleryPanel.qml
}
```

## Navigable row
```qml
CursorSurface {
  hasCursor: root.focusSection === "list" && root.selectedIndex === index
  current: modelData.connected
  onHovered: function(h) { if (h) { root.focusSection = "list"; root.selectedIndex = index } }
  Row { PanelActionButton { iconText: "󰆴"; hoverColor: Color.urgent; onClicked: forget() } }
}
```

## Test under themes
```bash
for t in lake-sunset catppuccin-latte flexoki-light white vantablack; do omarchy theme set $t; sleep 2; omarchy capture screenshot; done
omarchy theme set lake-sunset
```
