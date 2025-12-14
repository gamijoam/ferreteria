import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Rectangle {
    id: customerView
    // anchors.fill: parent managed by StackView
    color: "#f5f5f5"
    
    // State
    property int editingId: 0
    property string editingName: ""
    property string editingDoc: ""
    property string editingPhone: ""
    property string editingEmail: ""
    property string editingAddr: ""
    property real editingLimit: 0.0
    
    // --- CONNECTIONS ---
    Connections {
        target: customerBridge
        
        function onCustomersUpdated() {
            refreshList()
        }
        
        function onOperationSuccess(msg) {
            successDialog.text = msg
            successDialog.open()
            customerDialog.close()
        }
        
        function onOperationError(msg) {
            errorDialog.text = msg
            errorDialog.open()
        }
    }
    
    // Function to refresh list
    function refreshList() {
        var results = customerBridge.searchCustomers(searchField.text)
        customerListModel.clear()
        results.forEach(function(c) {
            customerListModel.append(c)
        })
    }
    
    Component.onCompleted: {
        refreshList()
    }
    
    // --- UI ---
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16
        
        // Header
        RowLayout {
            Layout.fillWidth: true
            
            Text {
                text: "👥 Gestión de Clientes"
                font.family: "Segoe UI"
                font.pixelSize: 24
                font.weight: Font.Bold
                color: "#333"
            }
            
            Item { Layout.fillWidth: true }
            
            AppButton {
                text: "+ Nuevo Cliente"
                variant: "primary"
                iconName: "👤"
                onClicked: {
                    editingId = 0
                    editingName = ""
                    editingDoc = ""
                    editingPhone = ""
                    editingEmail = ""
                    editingAddr = ""
                    editingLimit = 0.0
                    
                    nameInput.text = ""
                    docInput.text = ""
                    phoneInput.text = ""
                    emailInput.text = ""
                    addrInput.text = ""
                    limitInput.text = "0.00"
                    
                    customerDialog.title = "Nuevo Cliente"
                    customerDialog.open()
                }
            }
        }
        
        // Search Bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            color: "white"
            radius: 8
            border.width: 1
            border.color: "#e0e0e0"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 10
                
                Text { text: "🔍"; font.pixelSize: 16 }
                
                TextField {
                    id: searchField
                    Layout.fillWidth: true
                    placeholderText: "Buscar por nombre o documento..."
                    font.family: "Segoe UI"
                    font.pixelSize: 14
                    background: null
                    
                    onTextChanged: refreshList()
                }
            }
        }
        
        // List Header
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: "#E0E0E0"
            radius: 4
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                
                Text { Layout.preferredWidth: 60; text: "ID"; font.bold: true }
                Text { Layout.fillWidth: true; Layout.minimumWidth: 150; text: "Nombre"; font.bold: true }
                Text { Layout.preferredWidth: 100; text: "Documento"; font.bold: true }
                Text { Layout.preferredWidth: 100; text: "Teléfono"; font.bold: true }
                Text { Layout.preferredWidth: 80; text: "Balance"; font.bold: true; horizontalAlignment: Text.AlignRight }
                Text { Layout.preferredWidth: 100; text: "Acciones"; font.bold: true; horizontalAlignment: Text.AlignCenter }
            }
        }
        
        // Customer List
        ListView {
            id: customerListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 4
            
            model: ListModel { id: customerListModel }
            
            delegate: Rectangle {
                width: ListView.view.width
                height: 50
                color: "white"
                radius: 4
                border.width: 1
                border.color: "#EEEEEE"
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10
                    
                    Text { 
                        Layout.preferredWidth: 60
                        text: model.id
                        font.family: "Segoe UI"
                        color: "#666"
                    }
                    
                    Text { 
                        Layout.fillWidth: true
                        Layout.minimumWidth: 150
                        text: model.name
                        font.family: "Segoe UI"
                        font.bold: true
                        elide: Text.ElideRight
                    }
                    
                    Text { 
                        Layout.preferredWidth: 100
                        text: model.id_number
                        font.family: "Segoe UI"
                        elide: Text.ElideRight
                    }
                    
                    Text { 
                        Layout.preferredWidth: 100
                        text: model.phone
                        font.family: "Segoe UI"
                        elide: Text.ElideRight
                    }
                    
                    Text { 
                        Layout.preferredWidth: 80
                        text: "$" + model.balance.toFixed(2)
                        font.family: "Segoe UI"
                        font.bold: true
                        color: model.balance > 0 ? "#F44336" : "#4CAF50"
                        horizontalAlignment: Text.AlignRight
                    }
                    
                    RowLayout {
                        Layout.preferredWidth: 100
                        Layout.alignment: Qt.AlignCenter
                        spacing: 8
                        
                        Button {
                            text: "✏️"
                            Layout.preferredWidth: 30
                            onClicked: {
                                editingId = model.id
                                editingName = model.name
                                editingDoc = model.id_number
                                editingPhone = model.phone
                                editingEmail = model.email
                                editingAddr = model.address
                                editingLimit = model.credit_limit
                                
                                nameInput.text = editingName
                                docInput.text = editingDoc
                                phoneInput.text = editingPhone
                                emailInput.text = editingEmail
                                addrInput.text = editingAddr
                                limitInput.text = editingLimit.toFixed(2)
                                
                                customerDialog.title = "Editar Cliente"
                                customerDialog.open()
                            }
                        }
                        
                        Button {
                            text: "🗑️"
                            Layout.preferredWidth: 30
                            onClicked: {
                                confirmDeleteDialog.customerId = model.id
                                confirmDeleteDialog.open()
                            }
                        }
                    }
                }
            }
        }
    }
    
    // --- DIALOGS ---
    
    Dialog {
        id: customerDialog
        title: "Nuevo Cliente"
        modal: true
        anchors.centerIn: parent
        width: 400
        
        contentItem: ColumnLayout {
            spacing: 12
            
            TextField {
                id: nameInput
                Layout.fillWidth: true
                placeholderText: "Nombre Completo *"
            }
            
            TextField {
                id: docInput
                Layout.fillWidth: true
                placeholderText: "Cédula / Documento"
            }
            
            TextField {
                id: phoneInput
                Layout.fillWidth: true
                placeholderText: "Teléfono"
            }
            
            TextField {
                id: emailInput
                Layout.fillWidth: true
                placeholderText: "Email"
            }
            
            TextField {
                id: addrInput
                Layout.fillWidth: true
                placeholderText: "Dirección"
            }
            
            RowLayout {
                Text { text: "Límite de Crédito ($):" }
                TextField {
                    id: limitInput
                    Layout.fillWidth: true
                    text: "0.00"
                    validator: DoubleValidator { bottom: 0; decimals: 2; locale: "C" }
                }
            }
             
            RowLayout {
                Layout.fillWidth: true
                Layout.topMargin: 10
                
                Button {
                    text: "Cancelar"
                    Layout.fillWidth: true
                    onClicked: customerDialog.close()
                }
                
                Button {
                    text: "Guardar"
                    Layout.fillWidth: true
                    highlighted: true
                    onClicked: {
                        var limit = parseFloat(limitInput.text) || 0.0
                        
                        if (editingId === 0) {
                            customerBridge.createCustomer(
                                nameInput.text,
                                docInput.text,
                                phoneInput.text,
                                emailInput.text,
                                addrInput.text,
                                limit
                            )
                        } else {
                            customerBridge.updateCustomer(
                                editingId,
                                nameInput.text,
                                docInput.text,
                                phoneInput.text,
                                emailInput.text,
                                addrInput.text,
                                limit
                            )
                        }
                    }
                }
            }
        }
    }
    
    Dialog {
        id: confirmDeleteDialog
        title: "Confirmar Eliminación"
        modal: true
        anchors.centerIn: parent
        width: 350
        property int customerId: 0
        
        contentItem: ColumnLayout {
            spacing: 10
            Text { text: "¿Está seguro que desea eliminar este cliente?" }
            RowLayout {
                Layout.fillWidth: true
                Button {
                    text: "Cancelar"
                    onClicked: confirmDeleteDialog.close()
                }
                Button {
                    text: "Eliminar"
                    highlighted: true
                    onClicked: {
                        customerBridge.deleteCustomer(confirmDeleteDialog.customerId)
                        confirmDeleteDialog.close()
                    }
                }
            }
        }
    }
    
    Dialog {
        id: successDialog
        title: "Éxito"
        modal: true
        anchors.centerIn: parent
        width: 300
        property alias text: successMsg.text
        contentItem: ColumnLayout {
            Text { id: successMsg }
            Button { text: "Aceptar"; onClicked: successDialog.close(); Layout.alignment: Qt.AlignHCenter }
        }
    }
    
    Dialog {
        id: errorDialog
        title: "Error"
        modal: true
        anchors.centerIn: parent
        width: 350
        property alias text: errorMsg.text
        contentItem: ColumnLayout {
            Text { id: errorMsg; color: "red" }
            Button { text: "Aceptar"; onClicked: errorDialog.close(); Layout.alignment: Qt.AlignHCenter }
        }
    }
}
