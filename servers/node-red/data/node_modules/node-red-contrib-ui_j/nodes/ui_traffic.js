module.exports = function(RED) {
    var ui = require('../ui')(RED);

    function TrafficNode(config) {
        RED.nodes.createNode(this, config);
        var node = this;
        
        var tab = RED.nodes.getNode(config.tab);
        if (!tab) return;
        
        var done = ui.add({
            emitOnlyNewValues: false,
            node: node, 
            tab: tab, 
            group: config.group, 
            control: {
                type: 'traffic',
                label: config.name,
                order: config.order,
                format: config.format,
                green: false,
                red: false,
                orange: true
            },
            beforeSend: function (msg) {
                msg.topic = config.topic;
            }
        });

        node.on("close", done);
    }

    RED.nodes.registerType("ui_traffic", TrafficNode);
};