// POSView.qml - Point of Sale Interface
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Rectangle {
    id: posView
    anchors.fill: parent
    color: "#f5f5f5"
    
    // State variables
    property bool boxMode: false
    property bool creditMode: false
    property int selectedCustomerId: 0
    property string selectedCustomerName: ""
    
    // Header
    Rectangle {
        id: header
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 60
        color: "#2196F3"
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 16
            
            Text {
                text: "🛒 PUNTO DE VENTA"
                font.family: "Segoe UI"
                font.pixelSize: 20
                font.weight: Font.Bold
                color: "white"
            }
            
            Item { Layout.fillWidth: true }
            
            Rectangle {
                Layout.preferredWidth: 250
                Layout.preferredHeight: 35
                color: Qt.rgba(0, 0, 0, 0.2)
                radius: 4
                
                Text {
                    anchors.centerIn: parent
                    text: "Tasa: 1 USD = " + posBridge.exchangeRate.toFixed(2) + " Bs"
                    font.family: "Segoe UI"
                    font.pixelSize: 14
                    color: "white"
                }
            }
            
            Button {
                text: "← Volver"
                onClicked: stackView.pop()
                
                background: Rectangle {
                    color: parent.pressed ? "#1565C0" : (parent.hovered ? "#1976D2" : "transparent")
                    radius: 4
                    border.width: 1
                    border.color: "white"
                }
                
                contentItem: Text {
                    text: parent.text
                    font.family: "Segoe UI"
                    font.pixelSize: 14
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }
    
    // Main content
    RowLayout {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 16
        spacing: 16
        
        // LEFT PANEL (70%)
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: parent.width * 0.7
            spacing: 16
            
            // Search Bar
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 80
                color: "white"
                radius: 8
                border.width: 1
                border.color: "#e0e0e0"
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8
                    
                    Text {
                        text: "🔍 Buscar Producto (Enter para agregar)"
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                        font.weight: Font.Bold
                        color: "#666"
                    }
                    
                    TextField {
                        id: searchField
                        Layout.fillWidth: true
                        placeholderText: "Ingrese SKU o Nombre del Producto..."
                        font.family: "Segoe UI"
                        font.pixelSize: 16
                        
                        background: Rectangle {
                            color: "#f5f5f5"
                            radius: 4
                            border.width: searchField.activeFocus ? 2 : 1
                            border.color: searchField.activeFocus ? "#2196F3" : "#ddd"
                        }
                        
                        Keys.onReturnPressed: {
                            if (text.trim() !== "") {
                                posBridge.addToCart(text.trim(), 1.0, boxMode)
                                text = ""
                            }
                        }
                        
                        onTextChanged: {
                            if (text.length >= 2) {
                                var results = posBridge.searchProducts(text)
                                suggestionModel.clear()
                                results.forEach(function(item) {
                                    suggestionModel.append(item)
                                })
                                suggestionsPopup.visible = results.length > 0
                            } else {
                                suggestionsPopup.visible = false
                            }
                        }
                    }
                    
                    // Suggestions popup
                    Popup {
                        id: suggestionsPopup
                        y: searchField.height + 4
                        width: searchField.width
                        height: Math.min(suggestionList.contentHeight + 12, 350)
                        visible: false
                        
                        background: Rectangle {
                            color: "white"
                            border.width: 2
                            border.color: "#2196F3"
                            radius: 8
                            
                            layer.enabled: true
                            layer.effect: ShaderEffect {
                                property color shadowColor: Qt.rgba(0, 0, 0, 0.15)
                            }
                        }
                        
                        contentItem: ListView {
                            id: suggestionList
                            clip: true
                            spacing: 4
                            topMargin: 6
                            bottomMargin: 6
                            leftMargin: 6
                            rightMargin: 6
                            
                            model: ListModel { id: suggestionModel }
                            
                            delegate: Rectangle {
                                width: parent.width
                                height: 70
                                color: mouseArea.containsMouse ? "#E3F2FD" : "white"
                                radius: 6
                                border.width: 1
                                border.color: mouseArea.containsMouse ? "#2196F3" : "#e0e0e0"
                                
                                Behavior on color {
                                    ColorAnimation { duration: 150 }
                                }
                                
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 12
                                    
                                    // Product icon
                                    Rectangle {
                                        Layout.preferredWidth: 50
                                        Layout.preferredHeight: 50
                                        color: "#2196F3"
                                        radius: 6
                                        
                                        Text {
                                            anchors.centerIn: parent
                                            text: "📦"
                                            font.pixelSize: 24
                                        }
                                    }
                                    
                                    // Product info
                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 4
                                        
                                        // Product name
                                        Text {
                                            Layout.fillWidth: true
                                            text: model.name
                                            font.family: "Segoe UI"
                                            font.pixelSize: 14
                                            font.weight: Font.Bold
                                            color: "#333"
                                            elide: Text.ElideRight
                                        }
                                        
                                        // SKU and Location
                                        RowLayout {
                                            spacing: 8
                                            
                                            Text {
                                                text: model.sku ? "SKU: " + model.sku : ""
                                                font.family: "Segoe UI"
                                                font.pixelSize: 11
                                                color: "#666"
                                                visible: model.sku
                                            }
                                            
                                            Rectangle {
                                                width: 2
                                                height: 12
                                                color: "#ddd"
                                                visible: model.sku && model.location
                                            }
                                            
                                            Text {
                                                text: model.location ? "📍 " + model.location : ""
                                                font.family: "Segoe UI"
                                                font.pixelSize: 11
                                                color: "#666"
                                                visible: model.location
                                            }
                                        }
                                        
                                        // Price and Stock
                                        RowLayout {
                                            spacing: 12
                                            
                                            Text {
                                                text: "$" + model.price.toFixed(2)
                                                font.family: "Segoe UI"
                                                font.pixelSize: 13
                                                font.weight: Font.Bold
                                                color: "#4CAF50"
                                            }
                                            
                                            Rectangle {
                                                Layout.preferredWidth: stockText.width + 16
                                                Layout.preferredHeight: 22
                                                color: model.stock > 10 ? "#E8F5E9" : (model.stock > 0 ? "#FFF3E0" : "#FFEBEE")
                                                radius: 4
                                                
                                                Text {
                                                    id: stockText
                                                    anchors.centerIn: parent
                                                    text: "Stock: " + model.stock.toFixed(1)
                                                    font.family: "Segoe UI"
                                                    font.pixelSize: 11
                                                    font.weight: Font.Bold
                                                    color: model.stock > 10 ? "#2E7D32" : (model.stock > 0 ? "#F57C00" : "#C62828")
                                                }
                                            }
                                        }
                                    }
                                    
                                    // Add button
                                    Rectangle {
                                        Layout.preferredWidth: 40
                                        Layout.preferredHeight: 40
                                        color: mouseArea.containsMouse ? "#1976D2" : "#2196F3"
                                        radius: 20
                                        
                                        Text {
                                            anchors.centerIn: parent
                                            text: "+"
                                            font.pixelSize: 24
                                            font.weight: Font.Bold
                                            color: "white"
                                        }
                                    }
                                }
                                
                                MouseArea {
                                    id: mouseArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    
                                    onClicked: {
                                        searchField.text = model.name
                                        suggestionsPopup.visible = false
                                        posBridge.addToCart(model.name, 1.0, boxMode)
                                        searchField.text = ""
                                        searchField.forceActiveFocus()
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            // Shopping Cart Table
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "white"
                radius: 8
                border.width: 1
                border.color: "#e0e0e0"
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8
                    
                    Text {
                        text: "🛒 Carrito de Compras"
                        font.family: "Segoe UI"
                        font.pixelSize: 14
                        font.weight: Font.Bold
                        color: "#333"
                    }
                    
                    // Table Header
                    Rectangle {
                        Layout.fillWidth: true
                        height: 40
                        color: "#2196F3"
                        radius: 4
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 8
                            
                            Text { 
                                Layout.preferredWidth: 200
                                text: "Producto"
                                font.family: "Segoe UI"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: "white"
                            }
                            Text { 
                                Layout.preferredWidth: 80
                                text: "Cant."
                                font.family: "Segoe UI"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: "white"
                            }
                            Text { 
                                Layout.preferredWidth: 80
                                text: "Tipo"
                                font.family: "Segoe UI"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: "white"
                            }
                            Text { 
                                Layout.preferredWidth: 100
                                text: "Precio Unit."
                                font.family: "Segoe UI"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: "white"
                            }
                            Text { 
                                Layout.preferredWidth: 100
                                text: "Subtotal"
                                font.family: "Segoe UI"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: "white"
                            }
                            Text { 
                                Layout.preferredWidth: 80
                                text: "Acción"
                                font.family: "Segoe UI"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: "white"
                            }
                        }
                    }
                    
                    // Cart Items
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        
                        ListView {
                            id: cartList
                            model: posBridge.cart
                            spacing: 4
                            
                            delegate: Rectangle {
                                width: parent.width - 20
                                height: 60
                                color: ListView.isCurrentItem ? "#E3F2FD" : (index % 2 === 0 ? "#fafafa" : "white")
                                radius: 4
                                border.width: ListView.isCurrentItem ? 1 : 0
                                border.color: "#2196F3"
                                
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: cartList.currentIndex = index
                                    z: -1 // Ensure it's behind other interactive elements
                                }
                                
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 8
                                    
                                    Text {
                                        Layout.preferredWidth: 200
                                        text: modelData.name
                                        font.family: "Segoe UI"
                                        font.pixelSize: 13
                                        color: "#333"
                                        elide: Text.ElideRight
                                    }
                                    
                                    TextField {
                                        Layout.preferredWidth: 80
                                        text: modelData.quantity.toFixed(2)
                                        font.family: "Segoe UI"
                                        font.pixelSize: 13
                                        horizontalAlignment: Text.AlignRight
                                        
                                        background: Rectangle {
                                            color: "#f0f0f0"
                                            radius: 4
                                            border.width: parent.activeFocus ? 2 : 1
                                            border.color: parent.activeFocus ? "#2196F3" : "#ddd"
                                        }
                                        
                                        onEditingFinished: {
                                            var newQty = parseFloat(text)
                                            if (!isNaN(newQty) && newQty > 0) {
                                                posBridge.updateQuantity(index, newQty)
                                            }
                                        }
                                    }
                                    
                                    Text {
                                        Layout.preferredWidth: 80
                                        text: modelData.is_box ? "CAJA" : modelData.unit_type
                                        font.family: "Segoe UI"
                                        font.pixelSize: 12
                                        color: "#666"
                                    }
                                    
                                    Text {
                                        Layout.preferredWidth: 100
                                        text: "$" + modelData.unit_price.toFixed(2)
                                        font.family: "Segoe UI"
                                        font.pixelSize: 13
                                        color: "#333"
                                        horizontalAlignment: Text.AlignRight
                                    }
                                    
                                    Text {
                                        Layout.preferredWidth: 100
                                        text: "$" + modelData.subtotal.toFixed(2)
                                        font.family: "Segoe UI"
                                        font.pixelSize: 13
                                        font.weight: Font.Bold
                                        color: "#4CAF50"
                                        horizontalAlignment: Text.AlignRight
                                    }
                                    
                                    Button {
                                        Layout.preferredWidth: 80
                                        text: "Eliminar"
                                        
                                        background: Rectangle {
                                            color: parent.pressed ? "#D32F2F" : (parent.hovered ? "#F44336" : "#EF5350")
                                            radius: 4
                                        }
                                        
                                        contentItem: Text {
                                            text: parent.text
                                            font.family: "Segoe UI"
                                            font.pixelSize: 11
                                            color: "white"
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                        
                                        onClicked: posBridge.removeFromCart(index)
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            // Bottom: Total and Actions
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 80
                color: "white"
                radius: 8
                border.width: 1
                border.color: "#e0e0e0"
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 16
                    
                    Text {
                        text: "TOTAL: $" + posBridge.total.toFixed(2) + " / Bs " + posBridge.totalBs.toFixed(2)
                        font.family: "Segoe UI"
                        font.pixelSize: 24
                        font.weight: Font.Bold
                        color: "#4CAF50"
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Button {
                        text: "COBRAR"
                        Layout.preferredWidth: 150
                        Layout.preferredHeight: 50
                        enabled: posBridge.cart.length > 0
                        
                        background: Rectangle {
                            color: parent.enabled ? (parent.pressed ? "#1B5E20" : (parent.hovered ? "#2E7D32" : "#4CAF50")) : "#BDBDBD"
                            radius: 8
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.family: "Segoe UI"
                            font.pixelSize: 16
                            font.weight: Font.Bold
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            if (creditMode && selectedCustomerId === 0) {
                                errorDialog.errorText = "Debe seleccionar un cliente para venta a crédito"
                                errorDialog.open()
                                return
                            }
                            paymentDialog.open()
                        }
                    }
                }
            }
        }
        
        // RIGHT PANEL (30%) - Controls
        ScrollView {
            Layout.preferredWidth: parent.width * 0.3
            Layout.fillHeight: true
            clip: true
            contentWidth: availableWidth
            
            Column {
                width: parent.width
                spacing: 16
                topPadding: 16
                bottomPadding: 16
                
                // Sale Mode
                Rectangle {
                    width: parent.width - 32
                    height: saleModeContent.implicitHeight + 24
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: "white"
                    radius: 8
                    border.width: 1
                    border.color: "#e0e0e0"
                    
                    Column {
                        id: saleModeContent
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8
                        
                        Text {
                            width: parent.width
                            text: "Modo de Venta"
                            font.family: "Segoe UI"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: "#666"
                        }
                        
                        CheckBox {
                            id: boxModeCheck
                            width: parent.width
                            text: "Vender por Caja"
                            checked: boxMode
                            onCheckedChanged: boxMode = checked
                            
                            contentItem: Text {
                                text: parent.text
                                font.family: "Segoe UI"
                                font.pixelSize: 13
                                color: "#333"
                                leftPadding: parent.indicator.width + 8
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                }
                
                
                // Credit Sale
                Rectangle {
                    width: parent.width - 32
                    height: creditSaleContent.implicitHeight + 24
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: "white"
                    radius: 8
                    border.width: 1
                    border.color: creditMode ? "#F44336" : "#e0e0e0"
                    
                    Behavior on height {
                        NumberAnimation { duration: 200 }
                    }
                    
                    Column {
                        id: creditSaleContent
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8
                        
                        Text {
                            width: parent.width
                            text: "Tipo de Venta"
                            font.family: "Segoe UI"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: "#666"
                        }
                        
                        CheckBox {
                            id: creditCheck
                            width: parent.width
                            text: "Venta a Crédito (Fiado)"
                            checked: creditMode
                            onCheckedChanged: {
                                creditMode = checked
                                if (!checked) {
                                    selectedCustomerId = 0
                                    selectedCustomerName = ""
                                }
                            }
                            
                            contentItem: Text {
                                text: parent.text
                                font.family: "Segoe UI"
                                font.pixelSize: 13
                                font.weight: Font.Bold
                                color: "#D32F2F"
                                leftPadding: parent.indicator.width + 8
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                        
                        // Customer selection (visible only in credit mode)
                        Column {
                            visible: creditMode
                            width: parent.width
                            spacing: 4
                            
                            Text {
                                width: parent.width
                                text: "Cliente:"
                                font.family: "Segoe UI"
                                font.pixelSize: 11
                                color: "#666"
                            }
                            
                            TextField {
                                id: customerSearch
                                width: parent.width
                                placeholderText: "Buscar cliente..."
                                font.family: "Segoe UI"
                                font.pixelSize: 12
                                
                                background: Rectangle {
                                    color: "#f5f5f5"
                                    radius: 4
                                    border.width: parent.activeFocus ? 2 : 1
                                    border.color: parent.activeFocus ? "#2196F3" : "#ddd"
                                }
                                
                                onTextChanged: {
                                    if (text.length >= 2) {
                                        var results = posBridge.searchCustomers(text)
                                        customerModel.clear()
                                        results.forEach(function(item) {
                                            customerModel.append(item)
                                        })
                                        customerPopup.visible = results.length > 0
                                    } else {
                                        customerPopup.visible = false
                                    }
                                }
                            }
                            
                            // Customer suggestions
                            Popup {
                                id: customerPopup
                                y: customerSearch.height
                                width: customerSearch.width
                                height: Math.min(customerListView.contentHeight + 20, 200)
                                visible: false
                                
                                background: Rectangle {
                                    color: "white"
                                    border.width: 1
                                    border.color: "#ddd"
                                    radius: 4
                                }
                                
                                ListView {
                                    id: customerListView
                                    anchors.fill: parent
                                    anchors.margins: 4
                                    clip: true
                                    
                                    model: ListModel { id: customerModel }
                                    
                                    delegate: Rectangle {
                                        width: parent.width
                                        height: 40
                                        color: custMouseArea.containsMouse ? "#f0f0f0" : "white"
                                        
                                        Column {
                                            anchors.fill: parent
                                            anchors.margins: 6
                                            spacing: 2
                                            
                                            Text {
                                                text: model.name
                                                font.family: "Segoe UI"
                                                font.pixelSize: 12
                                                font.weight: Font.Bold
                                                color: "#333"
                                            }
                                            
                                            Text {
                                                text: (model.id_number ? "CI: " + model.id_number : "") + 
                                                      (model.phone ? " | Tel: " + model.phone : "")
                                                font.family: "Segoe UI"
                                                font.pixelSize: 10
                                                color: "#666"
                                            }
                                        }
                                        
                                        MouseArea {
                                            id: custMouseArea
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            
                                            onClicked: {
                                                selectedCustomerId = model.id
                                                selectedCustomerName = model.name
                                                customerSearch.text = model.name
                                                customerPopup.visible = false
                                            }
                                        }
                                    }
                                }
                            }
                            
                            Text {
                                width: parent.width
                                text: selectedCustomerId > 0 ? "✓ " + selectedCustomerName : "Ninguno seleccionado"
                                font.family: "Segoe UI"
                                font.pixelSize: 11
                                font.italic: selectedCustomerId === 0
                                color: selectedCustomerId > 0 ? "#4CAF50" : "#999"
                            }
                        }
                    }
                }
                
                // Discounts
                Rectangle {
                    width: parent.width - 32
                    height: discountsContent.implicitHeight + 24
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: "white"
                    radius: 8
                    border.width: 1
                    border.color: "#e0e0e0"
                    
                    Column {
                        id: discountsContent
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8
                        
                        Text {
                            width: parent.width
                            text: "Descuentos"
                            font.family: "Segoe UI"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: "#666"
                        }
                        
                        Button {
                            width: parent.width
                            text: "Descuento por Item"
                            
                            background: Rectangle {
                                color: parent.pressed ? "#7B1FA2" : (parent.hovered ? "#8E24AA" : "#9C27B0")
                                radius: 4
                            }
                            
                            contentItem: Text {
                                text: parent.text
                                font.family: "Segoe UI"
                                font.pixelSize: 12
                                color: "white"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            onClicked: {
                                if (cartList.currentIndex < 0) {
                                    errorDialog.errorText = "Seleccione un producto de la tabla"
                                    errorDialog.open()
                                    return
                                }
                                pinAuthDialog.requestAuthorization("aplicar descuento por ítem")
                            }
                        }
                        
                        Button {
                            width: parent.width
                            text: "Descuento Global"
                            
                            background: Rectangle {
                                color: parent.pressed ? "#5E35B1" : (parent.hovered ? "#673AB7" : "#7E57C2")
                                radius: 4
                            }
                            
                            contentItem: Text {
                                text: parent.text
                                font.family: "Segoe UI"
                                font.pixelSize: 12
                                color: "white"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            onClicked: pinAuthDialog.requestAuthorization("aplicar descuento global")
                        }
                        
                        Button {
                            width: parent.width
                            text: "⚡ Ajustar Total"
                            
                            background: Rectangle {
                                color: parent.pressed ? "#E64A19" : (parent.hovered ? "#F4511E" : "#FF5722")
                                radius: 4
                            }
                            
                            contentItem: Text {
                                text: parent.text
                                font.family: "Segoe UI"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: "white"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            onClicked: pinAuthDialog.requestAuthorization("ajustar total (descuento rápido)")
                        }
                    }
                }
                
                Item { height: 16 }
            }
        }
    }
    
    // Payment Dialog (will be created in next part)
    PaymentDialog {
        id: paymentDialog
    }
    
    // Discount Dialog

    
    // Error Dialog
    Dialog {
        id: errorDialog
        title: "Error"
        modal: true
        anchors.centerIn: parent
        
        property string errorText: ""
        
        contentItem: Text {
            text: errorDialog.errorText
            font.family: "Segoe UI"
            font.pixelSize: 14
            padding: 20
        }
        
        standardButtons: Dialog.Ok
    }
    
    // Success Dialog
    Dialog {
        id: successDialog
        title: "Venta Exitosa"
        modal: true
        anchors.centerIn: parent
        width: 400
        
        property string ticketText: ""
        
        contentItem: ScrollView {
            implicitHeight: 300
            
            Text {
                text: successDialog.ticketText
                font.family: "Courier New"
                font.pixelSize: 12
                padding: 20
            }
        }
        
        standardButtons: Dialog.Ok
        
        onAccepted: {
            searchField.forceActiveFocus()
        }
    }
    
    // Connections to POSBridge
    Connections {
        target: posBridge
        
        function onCartUpdated() {
            // Cart model updates automatically
        }
        
        function onSaleCompleted(saleId, ticket) {
            successDialog.ticketText = ticket
            successDialog.open()
        }
        
        function onSaleError(error) {
            errorDialog.errorText = error
            errorDialog.open()
        }
    }
    
    // Focus search field on load
    Component.onCompleted: {
        searchField.forceActiveFocus()
    }
    
    // Inline component for Payment Dialog
    component PaymentDialog: Dialog {
        id: payDlg
        title: "Forma de Pago"
        modal: true
        anchors.centerIn: parent
        width: 600
        height: 500
        
        property var paymentList: []
        
        contentItem: ColumnLayout {
            spacing: 16
            
            // Total display
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 60
                color: "#E8F5E9"
                radius: 8
                
                Text {
                    anchors.centerIn: parent
                    text: "TOTAL A PAGAR: $" + posBridge.total.toFixed(2) + " USD / Bs " + posBridge.totalBs.toFixed(2)
                    font.family: "Segoe UI"
                    font.pixelSize: 16
                    font.weight: Font.Bold
                    color: "#2E7D32"
                }
            }
            
            // For credit sales, just show confirm button
            Text {
                visible: creditMode
                Layout.fillWidth: true
                text: "Venta a crédito - No se requiere pago"
                font.family: "Segoe UI"
                font.pixelSize: 14
                font.italic: true
                color: "#666"
                horizontalAlignment: Text.AlignHCenter
            }
            
            // Payment controls (hidden for credit)
            ColumnLayout {
                visible: !creditMode
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 12
                
                Text {
                    text: "Métodos de Pago:"
                    font.family: "Segoe UI"
                    font.pixelSize: 13
                    font.weight: Font.Bold
                }
                
                // Payment list
                ScrollView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 150
                    clip: true
                    
                    ListView {
                        id: paymentListView
                        model: ListModel { id: paymentListModel }
                        spacing: 4
                        
                        delegate: Rectangle {
                            width: parent.width - 10
                            height: 40
                            color: "#f5f5f5"
                            radius: 4
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 8
                                
                                Text {
                                    Layout.fillWidth: true
                                    text: model.method
                                    font.family: "Segoe UI"
                                    font.pixelSize: 12
                                }
                                
                                Text {
                                    text: model.amount.toFixed(2) + " " + model.currency
                                    font.family: "Segoe UI"
                                    font.pixelSize: 12
                                    font.weight: Font.Bold
                                }
                                
                                Button {
                                    text: "X"
                                    Layout.preferredWidth: 30
                                    Layout.preferredHeight: 30
                                    
                                    background: Rectangle {
                                        color: parent.pressed ? "#C62828" : "#F44336"
                                        radius: 4
                                    }
                                    
                                    contentItem: Text {
                                        text: parent.text
                                        color: "white"
                                        horizontalAlignment: Text.AlignHCenter
                                        verticalAlignment: Text.AlignVCenter
                                    }
                                    
                                    onClicked: paymentListModel.remove(index)
                                }
                            }
                        }
                    }
                }
                
                // Add payment controls
                GridLayout {
                    Layout.fillWidth: true
                    columns: 2
                    rowSpacing: 8
                    columnSpacing: 12
                    
                    Text { text: "Método:"; font.family: "Segoe UI"; font.pixelSize: 12 }
                    ComboBox {
                        id: methodCombo
                        Layout.fillWidth: true
                        model: ["Efectivo", "Transferencia / Pago Móvil", "Tarjeta Débito/Crédito", "Zelle"]
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                    }
                    
                    Text { text: "Moneda:"; font.family: "Segoe UI"; font.pixelSize: 12 }
                    RowLayout {
                        RadioButton { id: rbBs; text: "Bs"; checked: true }
                        RadioButton { id: rbUsd; text: "USD" }
                    }
                    
                    Text { text: "Monto:"; font.family: "Segoe UI"; font.pixelSize: 12 }
                    TextField {
                        id: amountInput
                        Layout.fillWidth: true
                        text: posBridge.totalBs.toFixed(2)
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                        validator: DoubleValidator { bottom: 0; decimals: 2 }
                    }
                }
                
                Button {
                    Layout.fillWidth: true
                    text: "Agregar Pago"
                    
                    background: Rectangle {
                        color: parent.pressed ? "#2E7D32" : "#4CAF50"
                        radius: 4
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        font.family: "Segoe UI"
                        font.pixelSize: 13
                        font.weight: Font.Bold
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        var amount = parseFloat(amountInput.text)
                        if (isNaN(amount) || amount <= 0) {
                            errorDialog.errorText = "El monto debe ser mayor a 0"
                            errorDialog.open()
                            return
                        }
                        
                        var currency = rbUsd.checked ? "USD" : "Bs"
                        paymentListModel.append({
                            "method": methodCombo.currentText + " " + currency,
                            "amount": amount,
                            "currency": currency
                        })
                        
                        // Calculate remaining
                        var totalPaidUsd = 0
                        for (var i = 0; i < paymentListModel.count; i++) {
                            var p = paymentListModel.get(i)
                            if (p.currency === "USD") {
                                totalPaidUsd += p.amount
                            } else {
                                totalPaidUsd += p.amount / posBridge.exchangeRate
                            }
                        }
                        var remaining = posBridge.total - totalPaidUsd
                        if (rbBs.checked) {
                            amountInput.text = (remaining * posBridge.exchangeRate).toFixed(2)
                        } else {
                            amountInput.text = remaining.toFixed(2)
                        }
                    }
                }
            }
            
            Item { Layout.fillHeight: true }
        }
        
        standardButtons: Dialog.Ok | Dialog.Cancel
        
        onAccepted: {
            if (creditMode) {
                // Credit sale - no payments needed
                posBridge.finalizeSale([], selectedCustomerId, true)
            } else {
                // Cash sale - validate payments
                if (paymentListModel.count === 0) {
                    errorDialog.errorText = "Debe agregar al menos un método de pago"
                    errorDialog.open()
                    return
                }
                
                // Convert to array
                var payments = []
                for (var i = 0; i < paymentListModel.count; i++) {
                    var p = paymentListModel.get(i)
                    payments.push({
                        "method": p.method,
                        "amount": p.amount,
                        "currency": p.currency
                    })
                }
                
                posBridge.finalizeSale(payments, selectedCustomerId, false)
            }
            
            // Clear payment list
            paymentListModel.clear()
        }
        
        onRejected: {
            paymentListModel.clear()
        }
    }
    
    // --- PIN AUTHENTICATION ---
    PINAuthDialog {
        id: pinAuthDialog
        
        onAuthGranted: function(username, role) {
            console.log("Authorized: " + username + " (" + role + ") for " + actionDescription)
            
            if (actionDescription === "aplicar descuento global") {
                globalDiscountDialog.open()
            } else if (actionDescription === "aplicar descuento por ítem") {
                itemDiscountDialog.open()
            } else if (actionDescription === "ajustar total (descuento rápido)") {
                adjustTotalDialog.open()
            }
        }
    }
    
    // --- DISCOUNT DIALOGS ---
    
    // 1. Global Discount Dialog
    Dialog {
        id: globalDiscountDialog
        title: "Descuento Global"
        modal: true
        anchors.centerIn: parent
        width: 350
        
        contentItem: ColumnLayout {
            spacing: 16
            
            Text {
                text: "Tipo de descuento:"
                font.family: "Segoe UI"
                font.pixelSize: 13
            }
            
            ColumnLayout {
                RadioButton { id: rbGlobalPercent; text: "Porcentaje (%)"; checked: true }
                RadioButton { id: rbGlobalFixed; text: "Monto Fijo ($)" }
            }
            
            Text {
                text: "Valor:"
                font.family: "Segoe UI"
                font.pixelSize: 13
            }
            
            TextField {
                id: globalDiscountValue
                Layout.fillWidth: true
                text: "10"
                font.family: "Segoe UI"
                font.pixelSize: 14
                validator: DoubleValidator { bottom: 0; decimals: 2; locale: "C" }
            }
            
            RowLayout {
                Layout.fillWidth: true
                Item { Layout.fillWidth: true }
                Button {
                    text: "Cancelar"
                    onClicked: globalDiscountDialog.close()
                }
                Button {
                    text: "Aplicar"
                    highlighted: true
                    onClicked: globalDiscountDialog.accept()
                }
            }
        }
        
        onAccepted: {
            var value = parseFloat(globalDiscountValue.text)
            if (isNaN(value) || value <= 0) {
                errorDialog.errorText = "El valor debe ser mayor a 0"
                errorDialog.open()
                return
            }
            
            var type = rbGlobalPercent.checked ? "PERCENT" : "FIXED"
            var result = posBridge.applyGlobalDiscount(value, type)
            // Bridge returns success status which we could handle if needed
            globalDiscountValue.text = "10"
        }
    }
    
    // 2. Item Discount Dialog
    Dialog {
        id: itemDiscountDialog
        title: "Descuento por Item"
        modal: true
        anchors.centerIn: parent
        width: 350
        
        onOpened: {
            if (cartList.currentIndex < 0) {
                close()
                errorDialog.errorText = "Seleccione un producto de la tabla"
                errorDialog.open()
            }
        }
        
        contentItem: ColumnLayout {
            spacing: 16
            
            Text {
                text: "Tipo de descuento:"
                font.family: "Segoe UI"
                font.pixelSize: 13
            }
            
            ColumnLayout {
                RadioButton { id: rbItemPercent; text: "Porcentaje (%)"; checked: true }
                RadioButton { id: rbItemFixed; text: "Monto Fijo ($)" }
            }
            
            Text {
                text: "Valor:"
                font.family: "Segoe UI"
                font.pixelSize: 13
            }
            
            TextField {
                id: itemDiscountValue
                Layout.fillWidth: true
                text: "10"
                font.family: "Segoe UI"
                font.pixelSize: 14
                validator: DoubleValidator { bottom: 0; decimals: 2; locale: "C" }
            }
            
            RowLayout {
                Layout.fillWidth: true
                Item { Layout.fillWidth: true }
                Button {
                    text: "Cancelar"
                    onClicked: itemDiscountDialog.close()
                }
                Button {
                    text: "Aplicar"
                    highlighted: true
                    onClicked: itemDiscountDialog.accept()
                }
            }
        }
        
        onAccepted: {
            var value = parseFloat(itemDiscountValue.text)
            if (isNaN(value) || value <= 0) {
                errorDialog.errorText = "El valor debe ser mayor a 0"
                errorDialog.open()
                return
            }
            
            var type = rbItemPercent.checked ? "PERCENT" : "FIXED"
            posBridge.applyItemDiscount(cartList.currentIndex, value, type)
            itemDiscountValue.text = "10"
        }
    }
    
    // 3. Adjust Total Dialog
    Dialog {
        id: adjustTotalDialog
        title: "Ajustar Total"
        modal: true
        anchors.centerIn: parent
        width: 350
        
        property double currentTotalUsd: 0
        property double currentTotalBs: 0
        
        onOpened: {
            currentTotalUsd = posBridge.total
            currentTotalBs = posBridge.totalBs
            adjustTotalInput.text = currentTotalBs.toFixed(2)
            rbAdjustBs.checked = true
        }
        
        contentItem: ColumnLayout {
            spacing: 16
            
            Rectangle {
                Layout.fillWidth: true
                height: 60
                color: "#E3F2FD"
                radius: 4
                
                Text {
                    anchors.centerIn: parent
                    text: "Total actual:\n$" + adjustTotalDialog.currentTotalUsd.toFixed(2) + " / Bs " + adjustTotalDialog.currentTotalBs.toFixed(2)
                    horizontalAlignment: Text.AlignHCenter
                    font.family: "Segoe UI"
                    font.pixelSize: 13
                }
            }
            
            Text { text: "Moneda del nuevo total:"; font.family: "Segoe UI" }
            
            RowLayout {
                RadioButton { 
                    id: rbAdjustBs 
                    text: "Bs" 
                    checked: true 
                    onCheckedChanged: {
                        if (checked) adjustTotalInput.text = adjustTotalDialog.currentTotalBs.toFixed(2)
                    }
                }
                RadioButton { 
                    id: rbAdjustUsd 
                    text: "USD" 
                    onCheckedChanged: {
                        if (checked) adjustTotalInput.text = adjustTotalDialog.currentTotalUsd.toFixed(2)
                    }
                }
            }
            
            Text { text: "Nuevo Total:"; font.family: "Segoe UI" }
            
            TextField {
                id: adjustTotalInput
                Layout.fillWidth: true
                font.family: "Segoe UI"
                font.pixelSize: 14
                validator: DoubleValidator { bottom: 0; decimals: 2; locale: "C" }
            }
            
            RowLayout {
                Layout.fillWidth: true
                Item { Layout.fillWidth: true }
                Button {
                    text: "Cancelar"
                    onClicked: adjustTotalDialog.close()
                }
                Button {
                    text: "Aplicar"
                    highlighted: true
                    onClicked: adjustTotalDialog.accept()
                }
            }
        }
        
        onAccepted: {
            var newTotal = parseFloat(adjustTotalInput.text)
            if (isNaN(newTotal) || newTotal < 0) return
            
            var newTotalUsd = 0
            if (rbAdjustUsd.checked) {
                newTotalUsd = newTotal
                if (newTotalUsd >= adjustTotalDialog.currentTotalUsd) {
                    errorDialog.errorText = "El nuevo total debe ser menor al actual"
                    errorDialog.open()
                    return
                }
            } else {
                // Bs
                if (newTotal >= adjustTotalDialog.currentTotalBs) {
                    errorDialog.errorText = "El nuevo total debe ser menor al actual"
                    errorDialog.open()
                    return
                }
                newTotalUsd = newTotal / posBridge.exchangeRate
            }
            
            var discountUsd = adjustTotalDialog.currentTotalUsd - newTotalUsd
            posBridge.applyGlobalDiscount(discountUsd, "FIXED")
        }
    }
}
