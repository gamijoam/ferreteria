// ProductView.qml - Product Management Interface
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: productView
    // anchors.fill: parent (Handled by StackView)
    color: "#f5f5f5"
    
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
                text: "📦 GESTIÓN DE PRODUCTOS"
                font.family: "Segoe UI"
                font.pixelSize: 20
                font.weight: Font.Bold
                color: "white"
            }
            
            Item { Layout.fillWidth: true }
            
            Button {
                text: "+ Nuevo Producto"
                
                background: Rectangle {
                    color: parent.pressed ? "#2E7D32" : (parent.hovered ? "#388E3C" : "#4CAF50")
                    radius: 6
                }
                
                contentItem: Text {
                    text: parent.text
                    font.family: "Segoe UI"
                    font.pixelSize: 14
                    font.weight: Font.Bold
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    padding: 12
                }
                
                onClicked: {
                    productDialog.mode = "create"
                    productDialog.productId = 0
                    productDialog.clearForm()
                    productDialog.open()
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
    ColumnLayout {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 16
        spacing: 16
        
        // Search bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            color: "white"
            radius: 8
            border.width: 1
            border.color: "#e0e0e0"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12
                
                Text {
                    text: "🔍 Buscar:"
                    font.family: "Segoe UI"
                    font.pixelSize: 13
                    color: "#666"
                }
                
                TextField {
                    id: searchField
                    Layout.fillWidth: true
                    placeholderText: "Buscar por nombre o código..."
                    font.family: "Segoe UI"
                    font.pixelSize: 14
                    
                    background: Rectangle {
                        color: "#f5f5f5"
                        radius: 4
                        border.width: parent.activeFocus ? 2 : 1
                        border.color: parent.activeFocus ? "#2196F3" : "#ddd"
                    }
                    
                    onTextChanged: {
                        searchTimer.restart()
                    }
                }
                
                Timer {
                    id: searchTimer
                    interval: 500
                    repeat: false
                    onTriggered: {
                        productBridge.loadProducts(1, searchField.text)
                    }
                }
            }
        }
        
        // Product table
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
                
                // Table header
                Rectangle {
                    Layout.fillWidth: true
                    height: 40
                    color: "#2196F3"
                    radius: 4
                    
                    Row {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 4
                        
                        Text { 
                            width: 40
                            text: "ID"
                            font.family: "Segoe UI"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: "white"
                        }
                        Text { 
                            width: 180
                            text: "Nombre"
                            font.family: "Segoe UI"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: "white"
                        }
                        Text { 
                            width: 100
                            text: "SKU"
                            font.family: "Segoe UI"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: "white"
                        }
                        Text { 
                            width: 100
                            text: "Ubicación"
                            font.family: "Segoe UI"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: "white"
                        }
                        Text { 
                            width: 80
                            text: "Costo"
                            font.family: "Segoe UI"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: "white"
                        }
                        Text { 
                            width: 80
                            text: "Precio"
                            font.family: "Segoe UI"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: "white"
                        }
                        Text { 
                            width: 70
                            text: "Margen%"
                            font.family: "Segoe UI"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: "white"
                        }
                        Text { 
                            width: 70
                            text: "Stock"
                            font.family: "Segoe UI"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: "white"
                        }
                        Text { 
                            width: 60
                            text: "Min."
                            font.family: "Segoe UI"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: "white"
                        }
                        Text { 
                            width: 80
                            text: "Caja?"
                            font.family: "Segoe UI"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: "white"
                        }
                        Text { 
                            width: 150
                            text: "Acciones"
                            font.family: "Segoe UI"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: "white"
                        }
                    }
                }
                
                // Table content
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    
                    ListView {
                        id: productList
                        model: productBridge.products
                        spacing: 2
                        
                        delegate: Rectangle {
                            width: parent.width - 20
                            height: 50
                            color: index % 2 === 0 ? "#fafafa" : "white"
                            radius: 4
                            
                            Row {
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 4
                                
                                Text {
                                    width: 40
                                    text: modelData.id
                                    font.family: "Segoe UI"
                                    font.pixelSize: 11
                                    color: "#333"
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Text {
                                    width: 180
                                    text: modelData.name
                                    font.family: "Segoe UI"
                                    font.pixelSize: 11
                                    color: "#333"
                                    elide: Text.ElideRight
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Text {
                                    width: 100
                                    text: modelData.sku
                                    font.family: "Segoe UI"
                                    font.pixelSize: 11
                                    color: "#666"
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Text {
                                    width: 100
                                    text: modelData.location || "-"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 11
                                    color: "#666"
                                    elide: Text.ElideRight
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Text {
                                    width: 80
                                    text: "$" + modelData.cost_price.toFixed(2)
                                    font.family: "Segoe UI"
                                    font.pixelSize: 11
                                    color: "#333"
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Text {
                                    width: 80
                                    text: "$" + modelData.price.toFixed(2)
                                    font.family: "Segoe UI"
                                    font.pixelSize: 11
                                    color: "#333"
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Text {
                                    width: 70
                                    text: modelData.margin.toFixed(1) + "%"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 11
                                    font.weight: Font.Bold
                                    color: modelData.margin < 0 ? "#F44336" : "#4CAF50"
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Rectangle {
                                    width: 70
                                    height: 30
                                    color: modelData.low_stock ? "#FFEBEE" : "transparent"
                                    radius: 4
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData.stock.toFixed(1)
                                        font.family: "Segoe UI"
                                        font.pixelSize: 11
                                        font.weight: modelData.low_stock ? Font.Bold : Font.Normal
                                        color: modelData.low_stock ? "#D32F2F" : "#333"
                                    }
                                }
                                
                                Text {
                                    width: 60
                                    text: modelData.min_stock.toFixed(1)
                                    font.family: "Segoe UI"
                                    font.pixelSize: 11
                                    color: "#666"
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Text {
                                    width: 80
                                    text: modelData.is_box ? "Sí (" + modelData.conversion_factor + ")" : "No"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 11
                                    color: "#666"
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Row {
                                    width: 150
                                    spacing: 4
                                    
                                    Button {
                                        text: "✏️"
                                        width: 35
                                        height: 35
                                        
                                        background: Rectangle {
                                            color: parent.pressed ? "#1565C0" : (parent.hovered ? "#1976D2" : "#2196F3")
                                            radius: 4
                                        }
                                        
                                        contentItem: Text {
                                            text: parent.text
                                            font.pixelSize: 14
                                            color: "white"
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                        
                                        onClicked: {
                                            productDialog.mode = "edit"
                                            productDialog.productId = modelData.id
                                            productDialog.loadProduct(modelData)
                                            productDialog.open()
                                        }
                                    }
                                    
                                    Button {
                                        text: "🗑️"
                                        width: 35
                                        height: 35
                                        
                                        background: Rectangle {
                                            color: parent.pressed ? "#C62828" : (parent.hovered ? "#D32F2F" : "#F44336")
                                            radius: 4
                                        }
                                        
                                        contentItem: Text {
                                            text: parent.text
                                            font.pixelSize: 14
                                            color: "white"
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                        
                                        onClicked: {
                                            deleteDialog.productId = modelData.id
                                            deleteDialog.productName = modelData.name
                                            deleteDialog.open()
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Pagination
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            color: "white"
            radius: 8
            border.width: 1
            border.color: "#e0e0e0"
            
            RowLayout {
                anchors.centerIn: parent
                spacing: 16
                
                Button {
                    text: "◀ Anterior"
                    enabled: productBridge.currentPage > 1
                    
                    background: Rectangle {
                        color: parent.enabled ? (parent.pressed ? "#1565C0" : (parent.hovered ? "#1976D2" : "#2196F3")) : "#BDBDBD"
                        radius: 4
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        padding: 8
                    }
                    
                    onClicked: {
                        productBridge.loadProducts(productBridge.currentPage - 1, searchField.text)
                    }
                }
                
                Text {
                    text: "Página " + productBridge.currentPage + " de " + productBridge.totalPages + 
                          " (Total: " + productBridge.totalCount + ")"
                    font.family: "Segoe UI"
                    font.pixelSize: 13
                    color: "#333"
                }
                
                Button {
                    text: "Siguiente ▶"
                    enabled: productBridge.currentPage < productBridge.totalPages
                    
                    background: Rectangle {
                        color: parent.enabled ? (parent.pressed ? "#1565C0" : (parent.hovered ? "#1976D2" : "#2196F3")) : "#BDBDBD"
                        radius: 4
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        font.family: "Segoe UI"
                        font.pixelSize: 12
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        padding: 8
                    }
                    
                    onClicked: {
                        productBridge.loadProducts(productBridge.currentPage + 1, searchField.text)
                    }
                }
            }
        }
    }
    
    // Product Form Dialog
    ProductFormDialog {
        id: productDialog
    }
    
    // Delete Confirmation Dialog
    Dialog {
        id: deleteDialog
        title: "Confirmar Eliminación"
        modal: true
        anchors.centerIn: parent
        width: 400
        
        property int productId: 0
        property string productName: ""
        
        contentItem: Column {
            spacing: 16
            padding: 20
            
            Text {
                text: "¿Está seguro de eliminar este producto?"
                font.family: "Segoe UI"
                font.pixelSize: 14
                wrapMode: Text.WordWrap
                width: parent.width
            }
            
            Text {
                text: deleteDialog.productName
                font.family: "Segoe UI"
                font.pixelSize: 14
                font.weight: Font.Bold
                color: "#D32F2F"
                wrapMode: Text.WordWrap
                width: parent.width
            }
            
            Text {
                text: "El producto quedará inactivo pero se preservará el historial de ventas."
                font.family: "Segoe UI"
                font.pixelSize: 12
                font.italic: true
                color: "#666"
                wrapMode: Text.WordWrap
                width: parent.width
            }
        }
        
        standardButtons: Dialog.Yes | Dialog.No
        
        onAccepted: {
            productBridge.deleteProduct(productId)
        }
    }
    
    // Success/Error Dialogs
    Dialog {
        id: messageDialog
        modal: true
        anchors.centerIn: parent
        
        property string messageText: ""
        property bool isError: false
        
        title: isError ? "Error" : "Éxito"
        
        contentItem: Text {
            text: messageDialog.messageText
            font.family: "Segoe UI"
            font.pixelSize: 14
            padding: 20
        }
        
        standardButtons: Dialog.Ok
    }
    
    // Connections to ProductBridge
    Connections {
        target: productBridge
        
        function onProductsUpdated() {
            // Products list updates automatically
        }
        
        function onProductSuccess(message) {
            messageDialog.messageText = message
            messageDialog.isError = false
            messageDialog.open()
        }
        
        function onProductError(error) {
            messageDialog.messageText = error
            messageDialog.isError = true
            messageDialog.open()
        }
    }
    
    // Load products on startup
    Component.onCompleted: {
        productBridge.loadProducts(1, "")
    }
    
    // Inline component for Product Form Dialog
    component ProductFormDialog: Dialog {
        id: formDlg
        modal: true
        anchors.centerIn: parent
        width: 600
        height: 700
        
        property string mode: "create" // "create" or "edit"
        property int productId: 0
        
        title: mode === "create" ? "➕ Nuevo Producto" : "✏️ Editar Producto"
        
        function clearForm() {
            nameField.text = ""
            skuField.text = ""
            costField.text = "0"
            priceField.text = "0"
            stockField.text = "0"
            minStockField.text = "5"
            locationField.text = ""
            isBoxCheck.checked = false
            conversionField.text = "1"
            unitTypeCombo.currentIndex = 0
            calculateMargin()
        }
        
        function loadProduct(product) {
            nameField.text = product.name
            skuField.text = product.sku
            costField.text = product.cost_price.toString()
            priceField.text = product.price.toString()
            stockField.text = product.stock.toString()
            minStockField.text = product.min_stock.toString()
            locationField.text = product.location
            isBoxCheck.checked = product.is_box
            conversionField.text = product.conversion_factor.toString()
            unitTypeCombo.currentIndex = unitTypeCombo.find(product.unit_type)
            calculateMargin()
        }
        
        function calculateMargin() {
            var cost = parseFloat(costField.text) || 0
            var price = parseFloat(priceField.text) || 0
            
            if (price > 0) {
                var margin = ((price - cost) / price) * 100
                if (margin < 0) {
                    marginLabel.text = "Margen: " + margin.toFixed(1) + "% (PÉRDIDA)"
                    marginLabel.color = "#F44336"
                } else {
                    marginLabel.text = "Margen: " + margin.toFixed(1) + "%"
                    marginLabel.color = "#4CAF50"
                }
            } else {
                marginLabel.text = "Margen: -"
                marginLabel.color = "#999"
            }
        }
        
        background: Rectangle {
            color: "#f5f5f5"
            radius: 8
        }
        
        header: Rectangle {
            width: parent.width
            height: 60
            color: "#2196F3"
            radius: 8
            
            Text {
                anchors.centerIn: parent
                text: formDlg.title
                font.family: "Segoe UI"
                font.pixelSize: 18
                font.weight: Font.Bold
                color: "white"
            }
        }
        
        contentItem: ScrollView {
            clip: true
            contentWidth: availableWidth
            
            Column {
                width: parent.width
                spacing: 24
                topPadding: 24
                bottomPadding: 24
                leftPadding: 24
                rightPadding: 24
                
                // SECTION 1: Basic Information
                Rectangle {
                    width: parent.width - 48
                    height: basicInfoColumn.implicitHeight + 32
                    color: "white"
                    radius: 8
                    border.width: 1
                    border.color: "#e0e0e0"
                    
                    ColumnLayout {
                        id: basicInfoColumn
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 16
                        
                        Text {
                            text: "📝 Información Básica"
                            font.family: "Segoe UI"
                            font.pixelSize: 14
                            font.weight: Font.Bold
                            color: "#2196F3"
                        }
                        
                        // Name
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6
                            
                            Text { 
                                text: "Nombre del Producto *"
                                font.family: "Segoe UI"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: "#333"
                            }
                            TextField {
                                id: nameField
                                Layout.fillWidth: true
                                Layout.preferredHeight: 40
                                placeholderText: "Ej: Cemento Portland Tipo I"
                                font.family: "Segoe UI"
                                font.pixelSize: 13
                                
                                background: Rectangle {
                                    color: "#f9f9f9"
                                    radius: 4
                                    border.width: parent.activeFocus ? 2 : 1
                                    border.color: parent.activeFocus ? "#2196F3" : "#ddd"
                                }
                            }
                        }
                        
                        // SKU and Location in row
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 16
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 6
                                
                                Text { 
                                    text: "SKU / Código"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 12
                                    font.weight: Font.Bold
                                    color: "#333"
                                }
                                TextField {
                                    id: skuField
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    placeholderText: "Código único"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 13
                                    
                                    background: Rectangle {
                                        color: "#f9f9f9"
                                        radius: 4
                                        border.width: parent.activeFocus ? 2 : 1
                                        border.color: parent.activeFocus ? "#2196F3" : "#ddd"
                                    }
                                }
                            }
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 6
                                
                                Text { 
                                    text: "Ubicación"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 12
                                    font.weight: Font.Bold
                                    color: "#333"
                                }
                                TextField {
                                    id: locationField
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    placeholderText: "Ej: Estante A-1"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 13
                                    
                                    background: Rectangle {
                                        color: "#f9f9f9"
                                        radius: 4
                                        border.width: parent.activeFocus ? 2 : 1
                                        border.color: parent.activeFocus ? "#2196F3" : "#ddd"
                                    }
                                }
                            }
                        }
                    }
                }
                
                // SECTION 2: Pricing
                Rectangle {
                    width: parent.width - 48
                    height: pricingColumn.implicitHeight + 32
                    color: "white"
                    radius: 8
                    border.width: 1
                    border.color: "#e0e0e0"
                    
                    ColumnLayout {
                        id: pricingColumn
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 16
                        
                        Text {
                            text: "💰 Precios"
                            font.family: "Segoe UI"
                            font.pixelSize: 14
                            font.weight: Font.Bold
                            color: "#2196F3"
                        }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 16
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 6
                                
                                Text { 
                                    text: "Precio Costo"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 12
                                    font.weight: Font.Bold
                                    color: "#333"
                                }
                                TextField {
                                    id: costField
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    text: "0"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 13
                                    validator: DoubleValidator { 
                                        bottom: 0
                                        decimals: 2
                                        notation: DoubleValidator.StandardNotation
                                        locale: "C"
                                    }
                                    onTextChanged: formDlg.calculateMargin()
                                    
                                    background: Rectangle {
                                        color: "#f9f9f9"
                                        radius: 4
                                        border.width: parent.activeFocus ? 2 : 1
                                        border.color: parent.activeFocus ? "#2196F3" : "#ddd"
                                    }
                                }
                            }
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 6
                                
                                Text { 
                                    text: "Precio Venta *"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 12
                                    font.weight: Font.Bold
                                    color: "#333"
                                }
                                TextField {
                                    id: priceField
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    text: "0"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 13
                                    validator: DoubleValidator { 
                                        bottom: 0
                                        decimals: 2
                                        notation: DoubleValidator.StandardNotation
                                        locale: "C"
                                    }
                                    onTextChanged: formDlg.calculateMargin()
                                    
                                    background: Rectangle {
                                        color: "#f9f9f9"
                                        radius: 4
                                        border.width: parent.activeFocus ? 2 : 1
                                        border.color: parent.activeFocus ? "#2196F3" : "#ddd"
                                    }
                                }
                            }
                        }
                        
                        // Margin display
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 45
                            color: "#f0f0f0"
                            radius: 4
                            
                            Text {
                                id: marginLabel
                                anchors.centerIn: parent
                                text: "Margen: -"
                                font.family: "Segoe UI"
                                font.pixelSize: 15
                                font.weight: Font.Bold
                                color: "#999"
                            }
                        }
                    }
                }
                
                // SECTION 3: Inventory
                Rectangle {
                    width: parent.width - 48
                    height: inventoryColumn.implicitHeight + 32
                    color: "white"
                    radius: 8
                    border.width: 1
                    border.color: "#e0e0e0"
                    
                    ColumnLayout {
                        id: inventoryColumn
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 16
                        
                        Text {
                            text: "📦 Inventario"
                            font.family: "Segoe UI"
                            font.pixelSize: 14
                            font.weight: Font.Bold
                            color: "#2196F3"
                        }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 16
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 6
                                
                                Text { 
                                    text: "Stock Actual"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 12
                                    font.weight: Font.Bold
                                    color: "#333"
                                }
                                TextField {
                                    id: stockField
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    text: "0"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 13
                                    validator: DoubleValidator { 
                                        bottom: 0
                                        decimals: 3
                                        notation: DoubleValidator.StandardNotation
                                        locale: "C"
                                    }
                                    
                                    background: Rectangle {
                                        color: "#f9f9f9"
                                        radius: 4
                                        border.width: parent.activeFocus ? 2 : 1
                                        border.color: parent.activeFocus ? "#2196F3" : "#ddd"
                                    }
                                }
                            }
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 6
                                
                                Text { 
                                    text: "Stock Mínimo (Alerta)"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 12
                                    font.weight: Font.Bold
                                    color: "#333"
                                }
                                TextField {
                                    id: minStockField
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    text: "5"
                                    font.family: "Segoe UI"
                                    font.pixelSize: 13
                                    validator: DoubleValidator { 
                                        bottom: 0
                                        decimals: 3
                                        notation: DoubleValidator.StandardNotation
                                        locale: "C"
                                    }
                                    
                                    background: Rectangle {
                                        color: "#f9f9f9"
                                        radius: 4
                                        border.width: parent.activeFocus ? 2 : 1
                                        border.color: parent.activeFocus ? "#2196F3" : "#ddd"
                                    }
                                }
                            }
                        }
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6
                            
                            Text { 
                                text: "Tipo de Unidad"
                                font.family: "Segoe UI"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: "#333"
                            }
                            ComboBox {
                                id: unitTypeCombo
                                Layout.fillWidth: true
                                Layout.preferredHeight: 40
                                model: ["Unidad", "Metro", "Kilo", "Litro"]
                                font.family: "Segoe UI"
                                font.pixelSize: 13
                                
                                background: Rectangle {
                                    color: "#f9f9f9"
                                    radius: 4
                                    border.width: 1
                                    border.color: "#ddd"
                                }
                            }
                        }
                    }
                }
                
                // SECTION 4: Box/Pack Configuration
                Rectangle {
                    width: parent.width - 48
                    height: boxColumn.implicitHeight + 32
                    color: "white"
                    radius: 8
                    border.width: 1
                    border.color: "#e0e0e0"
                    
                    ColumnLayout {
                        id: boxColumn
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 16
                        
                        Text {
                            text: "📦 Configuración de Caja/Pack"
                            font.family: "Segoe UI"
                            font.pixelSize: 14
                            font.weight: Font.Bold
                            color: "#2196F3"
                        }
                        
                        CheckBox {
                            id: isBoxCheck
                            text: "Este producto se vende por Caja/Pack"
                            font.family: "Segoe UI"
                            font.pixelSize: 13
                        }
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6
                            visible: isBoxCheck.checked
                            
                            Text { 
                                text: "Unidades por Caja/Pack"
                                font.family: "Segoe UI"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: "#333"
                            }
                            TextField {
                                id: conversionField
                                Layout.fillWidth: true
                                Layout.preferredHeight: 40
                                text: "1"
                                font.family: "Segoe UI"
                                font.pixelSize: 13
                                enabled: isBoxCheck.checked
                                validator: IntValidator { bottom: 1 }
                                placeholderText: "Ej: 50 (50 unidades por caja)"
                                
                                background: Rectangle {
                                    color: parent.enabled ? "#f9f9f9" : "#f0f0f0"
                                    radius: 4
                                    border.width: parent.activeFocus ? 2 : 1
                                    border.color: parent.activeFocus ? "#2196F3" : "#ddd"
                                }
                            }
                        }
                    }
                }
            }
        }
        
        footer: Rectangle {
            width: parent.width
            height: 70
            color: "white"
            radius: 8
            
            RowLayout {
                anchors.centerIn: parent
                spacing: 12
                
                Button {
                    text: "Cancelar"
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: 45
                    
                    background: Rectangle {
                        color: parent.pressed ? "#999" : (parent.hovered ? "#bbb" : "#ccc")
                        radius: 6
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        font.family: "Segoe UI"
                        font.pixelSize: 14
                        color: "#333"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: formDlg.reject()
                }
                
                Button {
                    text: formDlg.mode === "create" ? "✓ Crear Producto" : "✓ Guardar Cambios"
                    Layout.preferredWidth: 180
                    Layout.preferredHeight: 45
                    
                    background: Rectangle {
                        color: parent.pressed ? "#1B5E20" : (parent.hovered ? "#2E7D32" : "#4CAF50")
                        radius: 6
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        font.family: "Segoe UI"
                        font.pixelSize: 14
                        font.weight: Font.Bold
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        if (!nameField.text.trim()) {
                            messageDialog.messageText = "El nombre es obligatorio"
                            messageDialog.isError = true
                            messageDialog.open()
                            return
                        }
                        
                        var name = nameField.text.trim()
                        var sku = skuField.text.trim()
                        var price = parseFloat(priceField.text)
                        var cost = parseFloat(costField.text)
                        var stock = parseFloat(stockField.text)
                        var minStock = parseFloat(minStockField.text)
                        var isBox = isBoxCheck.checked
                        var conversion = parseInt(conversionField.text)
                        var unitType = unitTypeCombo.currentText
                        var location = locationField.text.trim()
                        
                        if (formDlg.mode === "create") {
                            productBridge.createProduct(name, sku, price, cost, stock, minStock, 
                                                      isBox, conversion, unitType, location)
                        } else {
                            productBridge.updateProduct(formDlg.productId, name, sku, price, cost, stock, 
                                                      minStock, isBox, conversion, unitType, location)
                        }
                        
                        formDlg.accept()
                    }
                }
            }
        }
    }
}
