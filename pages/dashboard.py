import streamlit as st
from utils import (
    show_dashboard,
    show_dashboard_multi,
    show_interaction_pdp,
    show_interaction_pdp_multi,
    get_features,
    get_table_names,
    get_latest_row_and_metadata,
    train_model,
    train_model_multi,
    feature_importance,
    feature_importance_multi,
)

st.title("Dashboard")


def main():
    if not st.session_state.authentication_status:
        st.info("Please Login from the Home page and try again.")
        st.stop()

    user_id = st.session_state.user_id

    table_names = get_table_names(user_id)
    if not table_names:
        st.write("No tables found.")
        return

    default_table = (
        st.session_state.table_name
        if "table_name" in st.session_state
        and st.session_state.table_name in table_names
        else table_names[0]
    )
    selected_table = st.selectbox(
        "Select a table", table_names, index=table_names.index(default_table)
    )

    if selected_table:
        df, metadata = get_latest_row_and_metadata(user_id, selected_table)
        df = df.dropna()

        # Get the first N columns based on the length of session X_columns
        features = get_features(df)
        if len(metadata["output_column_names"]) == 2:
            features = features[:-1]

        # User input multibox select exactly 2 features to compare from the list of features
        selected_features = st.multiselect(
            "Select exactly 2 features to compare",
            options=features,
            default=features[:2],
        )

        # Check if exactly 2 features are selected
        if len(selected_features) != 2:
            st.error("Please select exactly 2 features.")

        else:
            # Once selected, the tuple of two features is added as pair_param
            pair_param = [tuple(selected_features)]

            directions = st.session_state.metadata["directions"]
            output_columns = st.session_state.metadata["output_column_names"]

            # TODO: save metadata to db, currently switching between single and multi will not work
            if len(output_columns) == 2:
                models = train_model_multi(df)
                show_dashboard_multi(
                    df,
                    models,
                    directions,
                    output_columns,
                )
                feature_importance_multi(df, models, output_columns)
                show_interaction_pdp_multi(
                    df,
                    pair_param,
                    models,
                    output_columns,
                    overlay=True,
                )
            else:
                model = train_model(df)
                show_dashboard(df, model, directions, output_columns)
                feature_importance(df, model)
                show_interaction_pdp(df, pair_param, model, overlay=True)


if __name__ == "__main__":
    main()
