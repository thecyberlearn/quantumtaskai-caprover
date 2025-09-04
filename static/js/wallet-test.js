/**
 * Quick wallet balance update test
 * Run this in browser console to test wallet balance updates
 */

function testWalletUpdate() {
    console.log('Testing wallet balance update...');
    
    // Get current balance from data attribute
    const currentBalance = parseFloat(document.body.getAttribute('data-user-balance') || '0');
    console.log('Current balance from data attribute:', currentBalance);
    
    // Get header balance element
    const headerBalance = document.querySelector('[data-wallet-balance]');
    console.log('Header balance element found:', !!headerBalance);
    if (headerBalance) {
        console.log('Current header text:', headerBalance.textContent);
    }
    
    // Test updating to a new balance
    const testBalance = currentBalance - 6.0;
    console.log('Testing update to:', testBalance);
    
    if (window.WorkflowsCore) {
        WorkflowsCore.updateWalletBalance(testBalance);
        console.log('✅ WorkflowsCore.updateWalletBalance() called');
        
        // Check if it worked
        if (headerBalance) {
            console.log('New header text:', headerBalance.textContent);
        }
        console.log('New data attribute:', document.body.getAttribute('data-user-balance'));
    } else {
        console.log('❌ WorkflowsCore not available');
    }
}

// Auto-run test
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', testWalletUpdate);
} else {
    testWalletUpdate();
}