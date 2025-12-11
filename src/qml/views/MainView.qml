// MainView.qml - Main Dashboard after login (Light Theme)
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: mainView
    anchors.fill: parent
    color: "#f5f5f5"  // Light gray background
    
    // Properties passed from login
    property string username: ""
    property string role: ""
    
    // Header
    Rectangle {
        id: header
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 80
        
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#2196F3" }
            GradientStop { position: 1.0; color: "#1976D2" }
        }
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 24
            
            // Business Logo
            Image {
                Layout.preferredWidth: 60
                Layout.preferredHeight: 60
                fillMode: Image.PreserveAspectFit
                source: authBridge.logoPath !== "" ? "file:///" + authBridge.logoPath : ""
                visible: authBridge.logoPath !== ""
            }
            
            // Business Name
            Text {
                Layout.fillWidth: true
                text: "🏪 " + authBridge.businessName.toUpperCase()
                font.family: "Segoe UI"
                font.pixelSize: 24
                font.weight: Font.Bold
                color: "white"
                verticalAlignment: Text.AlignVCenter
            }
            
            // User Info
            Text {
                text: "👤 " + mainView.username + " | " + mainView.role
                font.family: "Segoe UI"
                font.pixelSize: 14
                color: "white"
                verticalAlignment: Text.AlignVCenter
            }
        }
    }
    
    // Main Content Area
    ScrollView {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: footer.top
        anchors.margins: 32
        clip: true
        
        ColumnLayout {
            width: parent.parent.width - 64
            spacing: 32
            
            // Dashboard Button
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 120
                radius: 12
                color: "white"
                border.width: 1
                border.color: "#e0e0e0"
                
                // Shadow effect
                layer.enabled: true
                layer.effect: ShaderEffect {
                    property color shadowColor: Qt.rgba(0, 0, 0, 0.1)
                }
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 24
                    spacing: 24
                    
                    Text {
                        text: "📊"
                        font.pixelSize: 48
                    }
                    
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        
                        Text {
                            text: "DASHBOARD"
                            font.family: "Segoe UI"
                            font.pixelSize: 20
                            font.weight: Font.Bold
                            color: "#2196F3"
                        }
                        
                        Text {
                            text: "Vista general del negocio"
                            font.family: "Segoe UI"
                            font.pixelSize: 14
                            color: "#666"
                        }
                    }
                }
                
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                    
                    onEntered: parent.border.color = "#2196F3"
                    onExited: parent.border.color = "#e0e0e0"
                    onClicked: console.log("Dashboard clicked")
                }
            }
            
            // Module Grid Title
            Text {
                text: "Módulos del Sistema"
                font.family: "Segoe UI"
                font.pixelSize: 20
                font.weight: Font.DemiBold
                color: "#333"
            }
            
            // Module Grid
            Grid {
                Layout.fillWidth: true
                columns: 4
                rowSpacing: 20
                columnSpacing: 20
                
                // POS Module
                ModuleCard {
                    width: (parent.width - (3 * parent.columnSpacing)) / 4
                    height: 160
                    icon: "🛒"
                    title: "Punto de Venta"
                    subtitle: "Ventas rápidas"
                    cardColor: "#FF9800"
                    visible: mainView.role === "ADMIN" || mainView.role === "CASHIER"
                }
                
                // Products Module
                ModuleCard {
                    width: (parent.width - (3 * parent.columnSpacing)) / 4
                    height: 160
                    icon: "📦"
                    title: "Productos"
                    subtitle: "Gestión de productos"
                    cardColor: "#4CAF50"
                    visible: mainView.role === "ADMIN" || mainView.role === "WAREHOUSE"
                }
                
                // Inventory Module
                ModuleCard {
                    width: (parent.width - (3 * parent.columnSpacing)) / 4
                    height: 160
                    icon: "📥"
                    title: "Inventario"
                    subtitle: "Control de stock"
                    cardColor: "#4CAF50"
                    visible: mainView.role === "ADMIN" || mainView.role === "WAREHOUSE"
                }
                
                // Cash Module
                ModuleCard {
                    width: (parent.width - (3 * parent.columnSpacing)) / 4
                    height: 160
                    icon: "💵"
                    title: "Caja"
                    subtitle: "Control de efectivo"
                    cardColor: "#FF9800"
                    visible: mainView.role === "ADMIN" || mainView.role === "CASHIER"
                }
                
                // Customers Module
                ModuleCard {
                    width: (parent.width - (3 * parent.columnSpacing)) / 4
                    height: 160
                    icon: "👥"
                    title: "Clientes"
                    subtitle: "Crédito y pagos"
                    cardColor: "#9C27B0"
                    visible: mainView.role === "ADMIN" || mainView.role === "CASHIER"
                }
                
                // Reports Module
                ModuleCard {
                    width: (parent.width - (3 * parent.columnSpacing)) / 4
                    height: 160
                    icon: "📊"
                    title: "Reportes"
                    subtitle: "Análisis avanzado"
                    cardColor: "#00BCD4"
                    visible: mainView.role === "ADMIN"
                }
                
                // Config Module
                ModuleCard {
                    width: (parent.width - (3 * parent.columnSpacing)) / 4
                    height: 160
                    icon: "⚙️"
                    title: "Configuración"
                    subtitle: "Datos del negocio"
                    cardColor: "#607D8B"
                    visible: mainView.role === "ADMIN"
                }
                
                // Users Module
                ModuleCard {
                    width: (parent.width - (3 * parent.columnSpacing)) / 4
                    height: 160
                    icon: "👥"
                    title: "Usuarios"
                    subtitle: "Gestión de accesos"
                    cardColor: "#607D8B"
                    visible: mainView.role === "ADMIN"
                }
            }
            
            // Spacer at bottom
            Item { Layout.preferredHeight: 20 }
        }
    }
    
    // Footer
    Rectangle {
        id: footer
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 40
        color: "white"
        border.width: 1
        border.color: "#e0e0e0"
        
        Text {
            anchors.centerIn: parent
            text: "Sistema ERP v2.0 - PySide6 + QML"
            font.family: "Segoe UI"
            font.pixelSize: 12
            color: "#666"
        }
    }
    
    // ModuleCard Component (inline) - Square cards
    component ModuleCard: Rectangle {
        id: moduleCard
        
        property string icon: "📦"
        property string title: "Module"
        property string subtitle: "Description"
        property color cardColor: "#2196F3"
        
        signal clicked()
        
        radius: 12
        color: cardColor
        
        // Hover effect
        scale: mouseArea.containsMouse ? 1.03 : 1.0
        
        Behavior on scale {
            NumberAnimation { 
                duration: 200
                easing.type: Easing.OutCubic
            }
        }
        
        // Shadow
        layer.enabled: true
        layer.effect: ShaderEffect {
            property color shadowColor: Qt.rgba(0, 0, 0, 0.2)
        }
        
        ColumnLayout {
            anchors.centerIn: parent
            spacing: 12
            width: parent.width - 32
            
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: moduleCard.icon
                font.pixelSize: 48
            }
            
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: moduleCard.title
                font.family: "Segoe UI"
                font.pixelSize: 16
                font.weight: Font.Bold
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                width: parent.width
            }
            
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: moduleCard.subtitle
                font.family: "Segoe UI"
                font.pixelSize: 13
                color: Qt.rgba(1, 1, 1, 0.9)
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                width: parent.width
            }
        }
        
        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            
            onClicked: {
                moduleCard.clicked()
                console.log("Module clicked:", moduleCard.title)
            }
        }
    }
}
