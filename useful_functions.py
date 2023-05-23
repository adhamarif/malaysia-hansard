def get_coalition(df):
    """
    This function is used to get the coalition of the component party.
    The dataframe must have "current_party" column.
    """
    pn = ['PAS', 'BERSATU']
    ph = ['PKR', 'DAP', 'AMANAH', 'MUDA', 'UPKO']
    bn = ['UMNO', 'MIC', 'MCA', 'PBRS']

    coalition = []
    for i in df["current_party"]:
        if i in pn:
            coalition.append("Perikatan Nasional")
        elif i in ph:
            coalition.append("Pakatan Harapan")
        elif i in bn:
            coalition.append("Barisan Nasional")
        else:
            coalition.append("Other")
    
    return coalition