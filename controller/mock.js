var Piece = require('../model/piece');
var User = require('../model/user');


exports.addUser = function(req, res) {
    new User({
        name: 'elrrrrrrr', 
        avatar: 'http://tp1.sinaimg.cn/2017654444/50/5635300102/1', 
        work: true
    }).save(function(err,it) {
        res.send({'code':200})
    })
}

exports.clean = function(req, res) {

    Piece.remove(function() {})
    User.remove(function(){})

    return
}


exports.accessMock = function() {

    //fake user
    global.God = User.find()
    
}





