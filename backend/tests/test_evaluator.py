from backend.app.evaluator import evaluate_output, validate_output


def test_evaluator_returns_bounded_score():
    score = evaluate_output(
        "write a product launch announcement",
        "Product launch announcement: our platform is now available for customers.\nFeatures include automation and analytics.",
    )
    assert 0 <= score <= 1


def test_validation_rejects_empty_output():
    try:
        validate_output("")
        assert False
    except ValueError:
        assert True


def test_validation_accepts_reasonable_output():
    validate_output("This is a valid generated response with enough useful detail.")
