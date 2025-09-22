function complexFunction(param) {
    if (param.type === 'admin') {
        return param.data.map(item => ({
            id: item.id,
            name: item.name
        }));
    }
    return null;
}
