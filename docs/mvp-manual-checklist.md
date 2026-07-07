# MVP Manual Checklist

Use this checklist when handing off the repository or doing a local end-to-end sanity pass.

## Prep

1. Copy all `.env.example` files to `.env`.
2. Start backend.
3. Run backend migrations.
4. Seed backend data.
5. Start bot.
6. Start web app.

## Guest flow

1. Open the Mini App outside Telegram as a fresh guest.
2. Confirm the feed loads.
3. Open vacancy 1, 2, and 3.
4. Try to open vacancy 4.
5. Confirm paywall appears.
6. Open a vacancy as guest and tap apply.
7. Confirm the app routes to paywall/profile activation.
8. Confirm no HR contacts appear in feed or vacancy detail.

## Student auth, profile, payment, subscription, apply flow

1. Open the Mini App inside Telegram or a valid Telegram-compatible harness.
2. Confirm Telegram auth bootstrap succeeds.
3. Open `/profile`.
4. Save student profile data.
5. Open `/balance`.
6. Create a top-up for `350`.
7. Mock-confirm the payment.
8. Confirm subscription becomes active.
9. Open an active vacancy.
10. Apply.
11. Confirm the app returns to the feed.
12. Open `/applications`.
13. Confirm the new application appears.
14. Confirm student still does not see HR contacts.

## HR vacancy, payment, moderation, application flow

1. Open `/hr` as an active HR user.
2. Confirm dashboard loads vacancies and applications.
3. Create a vacancy.
4. Open the created vacancy detail.
5. Create publication payment.
6. Mock-confirm publication payment.
7. Confirm vacancy state updates.
8. Create one vacancy that should become `manual_review`.
9. Create one vacancy that should become `rejected`.
10. Open an HR application detail before acceptance.
11. Confirm no student contacts are visible.
12. Accept the application.
13. Confirm student contacts are now visible.

## Admin users, HR, moderation, complaints, payments, stats flow

1. Open `/admin` as non-admin and confirm access denied.
2. Open `/admin` as admin.
3. Open `/admin/users`.
4. Test block/unblock and mute/unmute.
5. Open `/admin/hr`.
6. Confirm HR profiles load and status updates work.
7. Open `/admin/moderation`.
8. Confirm manual-review vacancies appear.
9. Approve or reject one vacancy.
10. Open `/admin/complaints`.
11. Confirm complaint list loads and status update works.
12. Open `/admin/payments`.
13. Confirm payment rows are visible and read-only.
14. Open `/admin/stats`.
15. Confirm counters load.

## Bot menu smoke checks

1. Run `/start` as guest and confirm guest menu.
2. Run `/start` as student and confirm student menu.
3. Run `/start` as HR and confirm HR menu.
4. Run `/start` as admin and confirm admin menu.
5. Run `/help`.
6. Run `/profile`.
7. Run `/balance`.
8. Run `/support`.
9. Confirm web app buttons point to current routes.
10. Confirm callback placeholders respond safely without pretending to complete backend actions.

## Final pass conditions

Mark the local MVP pass successful if all of these are true:

- guest paywall works after 3 previews
- student can activate access and apply
- student never sees HR contacts
- HR sees student contacts only after acceptance
- admin operational pages load
- bot menus open the current Mini App routes
