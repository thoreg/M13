var m13 = angular.module('m13', []);

m13.config(function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});

m13.controller('NavigationController', ['$scope', 'transactionFactory', 'transactions',
                                     function ($scope, transactionFactory, transactions) {

    var self = this;

    $scope.years = ['2014', '2015', '2016'];
    $scope.months = [
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'
    ];
    $scope.transactions = transactions;

    transactionFactory.getTransactionsByYear('2015')
        .success(function(data) {
            self.display_result_on_success(data);
        })
        .error(function(data) {
            self.display_result_on_error(data);
        });


    self.reset = function() {
        $scope.resultAvailable = false;
        transactions.reset();
    };

    self.display_result_on_success = function(data) {
        $scope.loading = false;
        // $scope.resultAvailable = true;
        transactions.add_multiple_transactions(data);
        debugger
    };

    self.display_result_on_error = function(data) {
        $scope.loading = false;
        $scope.message = "Something fehlgeschlagen";
        console.log(data);
        debugger
    };

}]);
