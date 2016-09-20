/*******************************************************************************
*
* D3
*
*******************************************************************************/
angular.module('d3', [])
.factory('d3Service', ['$document', '$q', '$rootScope',
    function($document, $q, $rootScope) {
        var d = $q.defer();
        function onScriptLoad() {
            // Load client in the browser
            $rootScope.$apply(function() { d.resolve(window.d3); });
        }
        // Create a script tag with d3 as the source
        // and call our onScriptLoad callback when it
        // has been loaded
        var scriptTag = $document[0].createElement('script');
        scriptTag.type = 'text/javascript';
        scriptTag.async = true;
        scriptTag.src = 'http://d3js.org/d3.v3.min.js';
        scriptTag.onreadystatechange = function () {
            if (this.readyState == 'complete') onScriptLoad();
        }
        scriptTag.onload = onScriptLoad;

        var s = $document[0].getElementsByTagName('body')[0];
        s.appendChild(scriptTag);

        return {
            d3: function() { return d.promise; }
        };
}]);

/*******************************************************************************
*
* M13
*
*******************************************************************************/
var m13 = angular.module('m13', ['d3'])

.config(function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
})

.controller('NavigationController', ['$scope', 'transactionFactory', 'transactions',
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

}])

.directive('barChart', ['d3Service', function(d3Service) {
    return {
        restrict: 'EA',
        // directive code
    }
}]);
