

# (MFM) = ((Close - Low) - (High - Close)) / (High - low)
# (MFV) = MFM * Volume
def calculateAD(data):
    print(data)

    adl_sum = 0
    data_point_count = 0

    for i in range(data_point_count):
        todays_close = 0
        todays_high = 0
        todays_low = 0
        todays_volume = 0

        mvm = ((todays_close - todays_low) - (todays_high - todays_low)) / (todays_high - todays_low)
        mfv = mvm * todays_volume

        adl_sum += mfv

    return adl_sum

