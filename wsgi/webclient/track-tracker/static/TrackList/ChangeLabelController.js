app.controller('ChangeLabelController', function ($scope, $uibModalInstance, FeedReader, label)
{
    $scope.label = label;

    $scope.ok = function () {
        FeedReader.postTracks(label,$scope.new_label).then(function(x){
            $uibModalInstance.close($scope.new_label);
        })

    };

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
});