@app.route('/api/donations', methods=['POST'])
@jwt_required()
def create_donation():
    data = request.get_json()
    user_id = get_jwt_identity()['user_id']
    amount = data.get('amount')

    # Create a new donation
    new_donation = Donation(user_id=user_id, amount=amount)
    db.session.add(new_donation)
    db.session.commit()

    return jsonify({"msg": "Donation made successfully"}), 201

@app.route('/api/donations', methods=['GET'])
@jwt_required()
def get_donations():
    user_id = get_jwt_identity()['user_id']
    donations = Donation.query.filter_by(user_id=user_id).all()

    # Serialize the donations
    donation_list = [{"id": d.id, "amount": d.amount, "created_at": d.created_at} for d in donations]

    return jsonify(donations=donation_list), 200

@app.route('/api/donations/summary', methods=['GET'])
def get_donation_summary():
    total_amount = db.session.query(db.func.sum(Donation.amount)).scalar()
    total_donations = Donation.query.count()

    return jsonify({"total_amount": total_amount, "total_donations": total_donations}), 200
