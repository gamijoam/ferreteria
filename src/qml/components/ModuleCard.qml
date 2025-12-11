// ModuleCard.qml - Reusable Module Card Component
import QtQuick
import QtQuick.Layouts
import "../styles"

Rectangle {
    id: moduleCard
    
    property string icon: "📦"
    property string title: "Module"
    property string subtitle: "Description"
    property color cardColor: Theme.primary
    
    signal clicked()
    
    radius: Theme.radiusLg
    color: cardColor
    
    // Hover effect
    scale: mouseArea.containsMouse ? 1.05 : 1.0
    
    Behavior on scale {
        NumberAnimation { 
            duration: Theme.transitionNormal
            easing.type: Easing.OutCubic
        }
    }
    
    // Shadow
    layer.enabled: true
    layer.effect: ShaderEffect {
        property color shadowColor: Qt.rgba(0, 0, 0, 0.3)
    }
    
    ColumnLayout {
        anchors.centerIn: parent
        spacing: Theme.spacingSm
        
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: moduleCard.icon
            font.pixelSize: Theme.fontSize4xl
        }
        
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: moduleCard.title
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeLg
            font.weight: Theme.fontWeightBold
            color: "white"
            horizontalAlignment: Text.AlignHCenter
        }
        
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: moduleCard.subtitle
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
            color: Qt.rgba(1, 1, 1, 0.9)
            horizontalAlignment: Text.AlignHCenter
        }
    }
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        
        onClicked: moduleCard.clicked()
    }
}
