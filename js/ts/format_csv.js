export function formatTimestamp(timestamp){
    var stamp = timestamp.split(':')
    var min = Number(stamp[0])
    var second = Number(stamp[1]/60)
    var time = (min+second).toFixed(2)
    
    return Number(time)
}

export function formatScore(score, homeAway){
    var differential = score.split(':')
    
    
    if (homeAway == 0){
        return differential[1]-differential[0]
    } else {
        return differential[0]-differential[1]
    }
    
}