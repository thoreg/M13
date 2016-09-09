var Transaction = function(data) {
    /*
    if( data.customer ) {
        this.customer = data.customer;
        this.first_names = data.first_names;
        this.last_name = data.last_name;
        this.postal_code = data.postal_code;
        this.city = data.city;
        this.street = data.street;
        this.house_number = data.house_number;
    }
    */
};

// Data Store for transaction data
m13.factory('transactions', function() {
    var self = this;
    var transactions = [];
    var transactionService = {};

    transactionService.list = function() {
        return transactions;
    };

    transactionService.get_number_of_results = function() {
        return transactions.length;
    };

    transactionService.reset = function() {
        transactions = [];
        var transactionService = {};
    };

    transactionService.add_multiple_transactions = function(data) {
        for(var idx in data) {
            transactions.push(new Transaction(data[idx]));
        }
    };

    return transactionService;
});
