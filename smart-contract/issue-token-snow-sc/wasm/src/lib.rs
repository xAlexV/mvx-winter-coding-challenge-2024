// Code generated by the multiversx-sc build system. DO NOT EDIT.

////////////////////////////////////////////////////
////////////////// AUTO-GENERATED //////////////////
////////////////////////////////////////////////////

// Init:                                 1
// Upgrade:                              1
// Endpoints:                            2
// Async Callback:                       1
// Total number of exported functions:   5

#![no_std]

multiversx_sc_wasm_adapter::allocator!();
multiversx_sc_wasm_adapter::panic_handler!();

multiversx_sc_wasm_adapter::endpoints! {
    issue_token_snow_sc
    (
        init => init
        upgrade => upgrade
        issue_token_snow => issue_token_snow
        burn_token => burn_token
    )
}

multiversx_sc_wasm_adapter::async_callback! { issue_token_snow_sc }
