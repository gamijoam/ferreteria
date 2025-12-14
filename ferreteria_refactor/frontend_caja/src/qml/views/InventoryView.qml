// InventoryView.qml - Inventory Management (Bodega)
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
// Theme import removed to avoid syntax error

Rectangle {
    id: inventoryView
    // anchors.fill: parent (Handled by StackView)
    color: "#f5f5f5"
    
    // -- SHARED STATE --
    property int selectedProductId: 0
    property string selectedProductName: ""
    property string selectedProductSku: ""
    property double selectedProductStock: 0
    property string selectedProductUnit: ""
    property bool selectedProductIsBox: false
    property double selectedProductFactor: 1
    
    // For Stock Out
    property int outSelectedProductId: 0
    property string outSelectedProductName: ""
    property double outSelectedProductStock: 0
    property string outSelectedProductUnit: ""
    
    // Search State
    property string activeSearchContext: "ENTRY" // ENTRY, OUTPUT, HISTORY
    
    ListModel { id: searchResultsModel }
    ListModel { id: kardexModel }
    
    function performSearch(query) {
        if (query.length < 2) return
        
        var results = inventoryBridge.searchProducts(query)
        searchResultsModel.clear()
        for (var i = 0; i < results.length; i++) {
            searchResultsModel.append(results[i])
        }
        
        if (results.length > 0) {
            var targetItem = null
            if (activeSearchContext === "ENTRY") targetItem = entrySearch
            else if (activeSearchContext === "OUTPUT") targetItem = outputSearch
            else if (activeSearchContext === "HISTORY") targetItem = historySearch
            
            if (targetItem) {
                var mapPos = targetItem.mapToItem(inventoryView, 0, targetItem.height)
                searchPopup.x = mapPos.x
                searchPopup.y = mapPos.y + 5
                searchPopup.width = targetItem.width
                searchPopup.open()
            }
        }
    }
    
    // CONNECTIONS
    Connections {
        target: inventoryBridge
        
        function onInventoryUpdated() {
             // Clear forms
             entryQty.value = 1
             entrySearch.text = ""
             selectedProductId = 0
             
             outputQty.value = 1
             outputSearch.text = ""
             outSelectedProductId = 0
        }
        
        function onHistoryLoaded(data) {
            kardexModel.clear()
            for (var i = 0; i < data.length; i++) {
                kardexModel.append(data[i])
            }
        }
        
        function onOperationError(msg) {
             errorDialog.text = msg
             errorDialog.open()
        }
        
        function onOperationSuccess(msg) {
             successDialog.text = msg
             successDialog.open()
        }
    }
    
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
                text: "📦 GESTIÓN DE INVENTARIO (BODEGA)"
                font.family: "Segoe UI"
                font.pixelSize: 16
                font.weight: Font.Bold
                color: "white"
            }
            
            Item { Layout.fillWidth: true }
            
            AppButton {
                text: "← Volver"
                variant: "outlined"
                onClicked: stackView.pop()
                implicitHeight: 36
                
                background: Rectangle {
                    color: parent.pressed ? Qt.darker("#2196F3", 1.2) : "transparent"
                    radius: 4
                    border.width: 1
                    border.color: "white"
                }
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }
    
    // Main Content
    ColumnLayout {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 24
        spacing: 16
        
        // Tabs
        TabBar {
            id: bar
            width: parent.width
            Layout.fillWidth: true
            
            TabButton {
                text: "📥 ENTRADA DE MERCANCÍA"
                width: implicitWidth + 20
            }
            TabButton {
                text: "📤 SALIDA / AJUSTE"
                width: implicitWidth + 20
            }
            TabButton {
                text: "📜 KARDEX / HISTORIAL"
                width: implicitWidth + 20
            }
            
            onCurrentIndexChanged: {
                if (currentIndex === 2) {
                     // Load history logic if needed
                }
            }
        }
        
        StackLayout {
            width: parent.width
            currentIndex: bar.currentIndex
            Layout.fillHeight: true
            
            // --- TAB 1: ENTRADA ---
            Rectangle {
                color: "white"
                radius: 8
                border.width: 1
                border.color: "#e0e0e0"
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 40
                    spacing: 20
                    
                    Text {
                        text: "Registrar Compra / Entrada de Stock"
                        font.pixelSize: 16
                        font.weight: Font.Bold
                    }
                    
                    // Product Search
                    AppTextField {
                        id: entrySearch
                        Layout.fillWidth: true
                        placeholderText: "Buscar producto por nombre o SKU..."
                        iconLeft: "🔍"
                        
                        onTextChanged: {
                             activeSearchContext = "ENTRY"
                             performSearch(text)
                        }
                    }
                    
                    // Product Details
                    Rectangle {
                        Layout.fillWidth: true
                        height: 100
                        color: inventoryView.selectedProductId ? "#E8F5E9" : "#F5F5F5"
                        radius: 4
                        border.color: inventoryView.selectedProductId ? "#4CAF50" : "#E0E0E0"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 15
                            
                            Text {
                                text: inventoryView.selectedProductId ? inventoryView.selectedProductName : "Ningún producto seleccionado"
                                font.weight: Font.Bold
                                font.pixelSize: 14
                                color: inventoryView.selectedProductId ? "#4CAF50" : "#666"
                            }
                            
                            Text {
                                text: inventoryView.selectedProductId ? "Stock Actual: " + inventoryView.selectedProductStock + " " + inventoryView.selectedProductUnit : "-"
                                font.pixelSize: 14
                            }
                            
                            Text {
                                visible: inventoryView.selectedProductId && inventoryView.selectedProductSku !== ""
                                text: "SKU: " + inventoryView.selectedProductSku
                                font.pixelSize: 12
                                color: "#666"
                            }
                        }
                    }
                    
                    // Form
                    RowLayout {
                        spacing: 20
                        visible: inventoryView.selectedProductId > 0
                        
                        ColumnLayout {
                            Text { text: "Cantidad" }
                            SpinBox {
                                id: entryQty
                                from: 1
                                to: 100000
                                value: 1
                                editable: true
                            }
                        }
                        
                        CheckBox {
                            id: boxCheck
                            text: inventoryView.selectedProductIsBox ? 
                                  "Es Caja " + "(x" + inventoryView.selectedProductFactor + ")" : 
                                  "Es Caja / Pack"
                            enabled: inventoryView.selectedProductIsBox
                        }
                    }
                    
                    AppButton {
                        text: "REGISTRAR ENTRADA"
                        variant: "success"
                        Layout.alignment: Qt.AlignRight
                        enabled: inventoryView.selectedProductId > 0
                        onClicked: {
                            inventoryBridge.addStock(
                                inventoryView.selectedProductId, 
                                parseFloat(entryQty.value), 
                                boxCheck.checked
                            )
                        }
                    }
                    
                    Item { Layout.fillHeight: true }
                }
            }
            
            // --- TAB 2: SALIDA ---
            Rectangle {
                color: "white"
                radius: 8
                border.width: 1
                border.color: "#e0e0e0"
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 40
                    spacing: 20
                    
                    Text {
                        text: "Registrar Salida / Merma / Ajuste"
                        font.pixelSize: 16
                        font.weight: Font.Bold
                    }
                    
                    // Product Search
                    AppTextField {
                        id: outputSearch
                        Layout.fillWidth: true
                        placeholderText: "Buscar producto por nombre o SKU..."
                        iconLeft: "🔍"
                        
                        onTextChanged: {
                             activeSearchContext = "OUTPUT"
                             performSearch(text)
                        }
                    }
                    
                    // Product Details
                    Rectangle {
                        Layout.fillWidth: true
                        height: 100
                        color: inventoryView.outSelectedProductId ? "#FFEBEE" : "#F5F5F5"
                        radius: 4
                        border.color: inventoryView.outSelectedProductId ? "#F44336" : "#E0E0E0"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 15
                            
                            Text {
                                text: inventoryView.outSelectedProductId ? inventoryView.outSelectedProductName : "Ningún producto seleccionado"
                                font.weight: Font.Bold
                                font.pixelSize: 14
                                color: inventoryView.outSelectedProductId ? "#F44336" : "#666"
                            }
                            
                            Text {
                                text: inventoryView.outSelectedProductId ? "Stock Actual: " + inventoryView.outSelectedProductStock + " " + inventoryView.outSelectedProductUnit : "-"
                                font.pixelSize: 14
                            }
                        }
                    }
                    
                    // Form
                    RowLayout {
                        spacing: 20
                        visible: inventoryView.outSelectedProductId > 0
                        
                        ColumnLayout {
                            Text { text: "Cantidad a Retirar" }
                            SpinBox {
                                id: outputQty
                                from: 1
                                to: 100000
                                value: 1
                                editable: true
                            }
                        }
                        
                        ColumnLayout {
                            Text { text: "Motivo" }
                            ComboBox {
                                id: reasonCombo
                                model: ["Ajuste de Inventario", "Merma / Dañado", "Donación", "Uso Interno", "Otro"]
                                editable: true
                                implicitWidth: 200
                            }
                        }
                    }
                    
                    AppButton {
                        text: "REGISTRAR SALIDA"
                        variant: "danger"
                        Layout.alignment: Qt.AlignRight
                        enabled: inventoryView.outSelectedProductId > 0
                        onClicked: {
                             inventoryBridge.removeStock(
                                 inventoryView.outSelectedProductId,
                                 parseFloat(outputQty.value),
                                 reasonCombo.currentText
                             )
                        }
                    }
                    
                    Item { Layout.fillHeight: true }
                }
            }
            
            // --- TAB 3: KARDEX ---
            Rectangle {
                color: "white"
                radius: 8
                border.width: 1
                border.color: "#e0e0e0"
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16
                    
                    RowLayout {
                        Layout.fillWidth: true
                        
                        AppTextField {
                            id: historySearch
                            Layout.fillWidth: true
                            placeholderText: "Filtrar por producto..."
                            iconLeft: "🔍"
                            
                            onTextChanged: {
                                activeSearchContext = "HISTORY"
                                performSearch(text)
                            }
                        }
                        
                        AppButton {
                            text: "Ver Todos"
                            variant: "secondary"
                            // Mockup logic for now, or call bridge if implemented
                            onClicked: inventoryBridge.getKardex(0)
                        }
                    }
                    
                    // Table Header
                    RowLayout {
                        spacing: 0
                        height: 40
                        
                        Repeater {
                            model: ["Fecha", "Producto", "Tipo", "Cant.", "Saldo", "Motivo"]
                            delegate: Rectangle {
                                width: index === 0 ? 150 : (index === 1 ? 250 : (index === 5 ? 300 : 100))
                                height: 40
                                color: "#2196F3"
                                border.width: 1
                                border.color: "#1976D2"
                                Layout.fillWidth: index === 5
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: modelData
                                    color: "white"
                                    font.weight: Font.Bold
                                }
                            }
                        }
                    }
                    
                    // Table Content
                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: kardexModel
                        clip: true
                        
                        delegate: Rectangle {
                            width: parent.width
                            height: 40
                            color: index % 2 === 0 ? "white" : "#F9F9F9"
                            
                            RowLayout {
                                anchors.fill: parent
                                spacing: 0
                                
                                // Date
                                Text { 
                                    text: model.date 
                                    width: 150
                                    Layout.preferredWidth: 150
                                    leftPadding: 10
                                }
                                
                                // Product
                                Text { 
                                    text: model.product_name
                                    width: 250
                                    Layout.preferredWidth: 250
                                    elide: Text.ElideRight
                                }
                                
                                // Type
                                Rectangle {
                                    width: 100
                                    Layout.preferredWidth: 100
                                    height: 24
                                    radius: 12
                                    color: {
                                        if (model.type === "PURCHASE") return "#E8F5E9"
                                        if (model.type === "SALE") return "#FFEBEE"
                                        return "#FFF9C4"
                                    }
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: model.type
                                        font.pixelSize: 11
                                        font.weight: Font.Bold
                                        color: {
                                            if (model.type === "PURCHASE") return "#2E7D32"
                                            if (model.type === "SALE") return "#C62828"
                                            return "#F9A825"
                                        }
                                    }
                                }
                                
                                // Quantity
                                Text { 
                                    width: 100
                                    Layout.preferredWidth: 100
                                    text: (model.quantity > 0 ? "+" : "") + model.quantity
                                    color: model.quantity > 0 ? "green" : "red"
                                    horizontalAlignment: Text.AlignHCenter
                                }
                                
                                // Balance
                                Text { 
                                    width: 100
                                    Layout.preferredWidth: 100
                                    text: model.balance.toFixed(2)
                                    horizontalAlignment: Text.AlignHCenter
                                }
                                
                                // Desc
                                Text { 
                                    Layout.fillWidth: true
                                    text: model.description
                                    elide: Text.ElideRight
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    // --- SEARCH POPUP ---
    Popup {
        id: searchPopup
        height: 300
        padding: 0
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        
        background: Rectangle {
            color: "white"
            border.width: 1
            border.color: "#e0e0e0"
            radius: 4
            // layer.enabled: true
            // layer.effect: ShaderEffect { ... }
        }
        
        ListView {
            anchors.fill: parent
            model: searchResultsModel
            clip: true
            
            delegate: ItemDelegate {
                width: parent.width
                
                contentItem: ColumnLayout {
                    Text { 
                        text: model.name 
                        font.bold: true
                    }
                    Text { 
                        text: "SKU: " + model.sku + " | Stock: " + model.stock 
                        font.pixelSize: 12
                        color: "#666"
                    }
                }
                
                onClicked: {
                    if (activeSearchContext === "ENTRY") {
                        selectedProductId = model.id
                        selectedProductName = model.name
                        selectedProductSku = model.sku
                        selectedProductStock = model.stock
                        selectedProductUnit = model.unit_type
                        selectedProductIsBox = model.is_box
                        selectedProductFactor = model.conversion_factor
                        entrySearch.text = model.name
                    } else if (activeSearchContext === "OUTPUT") {
                        outSelectedProductId = model.id
                        outSelectedProductName = model.name
                        outSelectedProductStock = model.stock
                        outSelectedProductUnit = model.unit_type
                        outputSearch.text = model.name
                    } else if (activeSearchContext === "HISTORY") {
                        historySearch.text = model.name
                        inventoryBridge.getKardex(model.id)
                    }
                    searchPopup.close()
                }
            }
        }
    }
    
    // Dialogs
    Dialog {
        id: successDialog
        title: "Éxito"
        width: 300
        property alias text: msgLabel.text
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok
        
        ColumnLayout {
            anchors.fill: parent
            Text { id: msgLabel; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        }
    }
    
    Dialog {
        id: errorDialog
        title: "Error"
        width: 300
        property alias text: errMsgLabel.text
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok
        
        ColumnLayout {
            anchors.fill: parent
            Text { id: errMsgLabel; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: "red" }
        }
    }
}
