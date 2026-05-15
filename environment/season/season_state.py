




from enum import Enum


class Season(Enum):
    SPRING = 0
    SUMMER = 1
    AUTUMN = 2
    WINTER = 3



SEASON_EFFECT = {

    Season.SPRING: {
        "temp": 5,
        "rain": 1.3,
        "sun": 0.8
    },

    Season.SUMMER: {
        "temp": 12,
        "rain": 1.1,
        "sun": 1.2
    },

    Season.AUTUMN: {
        "temp": 3,
        "rain": 1.2,
        "sun": 0.7
    },

    Season.WINTER: {
        "temp": -8,
        "rain": 0.6,
        "sun": 0.4
    }
}
