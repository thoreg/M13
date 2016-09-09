m13.factory('transactionFactory', ['$http', function($http) {

    var urlBase = '/api/transactions/';
    var dataFactory = {};

    dataFactory.getTransactionsByYear = function (year) {
        return $http.get(urlBase, { params: { "year": year }});
    };

    return dataFactory;
}]);
