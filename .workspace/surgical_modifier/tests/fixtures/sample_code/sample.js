function complexFunction() {
    const nested = {
        property: "value",
        method: function() {
            return this.property;
        }
    };
    if (nested.property) {
        console.log("JavaScript pattern");
    }
}
